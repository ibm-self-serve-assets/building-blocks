// backend/src/features_1_2_3_4_14.js
const express = require("express");
const db = require("./db");
const jwt = require("jsonwebtoken");

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || "changeme-in-prod";

// How long a login counts as "active" (in minutes) for real-time metric
const ACTIVE_WINDOW_MINUTES = 5;

/* ------------------------------------------------------------------
 * Shared auth helpers (for these feature routes only)
 * -----------------------------------------------------------------*/

function authMiddleware(req, res, next) {
  const header = req.headers["authorization"];
  if (!header) {
    return res.status(401).json({ message: "Missing Authorization header" });
  }

  const [scheme, token] = header.split(" ");
  if (scheme !== "Bearer" || !token) {
    return res.status(401).json({ message: "Invalid Authorization header" });
  }

  try {
    const payload = jwt.verify(token, JWT_SECRET);
    req.user = {
      id: payload.userId,
      username: payload.username,
      is_admin: payload.is_admin || false
    };
    next();
  } catch (err) {
    return res.status(401).json({ message: "Invalid or expired token" });
  }
}

function adminOnly(req, res, next) {
  if (!req.user || !req.user.is_admin) {
    return res.status(403).json({ message: "Admin access required" });
  }
  next();
}

/* ==================================================================
 * 1) Wishlist
 * =================================================================*/

router.get("/wishlist", authMiddleware, async (req, res) => {
  try {
    const result = await db.query(
      `SELECT wi.id AS wishlist_item_id,
              p.id  AS product_id,
              p.name,
              p.price,
              p.image_url,
              p.category
       FROM wishlist_items wi
       JOIN products p ON wi.product_id = p.id
       WHERE wi.user_id = $1
       ORDER BY wi.created_at DESC`,
      [req.user.id]
    );
    res.json(result.rows);
  } catch (err) {
    console.error("Get wishlist error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.post("/wishlist", authMiddleware, async (req, res) => {
  const { productId } = req.body || {};
  if (!productId) {
    return res.status(400).json({ message: "productId is required" });
  }

  try {
    await db.query(
      `INSERT INTO wishlist_items (user_id, product_id)
       VALUES ($1, $2)
       ON CONFLICT (user_id, product_id) DO NOTHING`,
      [req.user.id, productId]
    );
    res.status(201).json({ message: "Added to wishlist" });
  } catch (err) {
    console.error("Add wishlist error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.delete("/wishlist/:productId", authMiddleware, async (req, res) => {
  const productId = req.params.productId;
  try {
    await db.query(
      "DELETE FROM wishlist_items WHERE user_id = $1 AND product_id = $2",
      [req.user.id, productId]
    );
    res.json({ message: "Removed from wishlist" });
  } catch (err) {
    console.error("Remove wishlist error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

/* ==================================================================
 * 2) Product Reviews & Ratings
 * =================================================================*/

router.get("/products/:id/reviews", async (req, res) => {
  const productId = req.params.id;
  try {
    const result = await db.query(
      `SELECT r.id,
              r.rating,
              r.comment,
              r.created_at,
              u.username
       FROM product_reviews r
       JOIN users u ON r.user_id = u.id
       WHERE r.product_id = $1
       ORDER BY r.created_at DESC`,
      [productId]
    );
    res.json(result.rows);
  } catch (err) {
    console.error("Get reviews error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.post("/products/:id/reviews", authMiddleware, async (req, res) => {
  const productId = req.params.id;
  const { rating, comment } = req.body || {};
  const r = Number(rating);

  if (!r || r < 1 || r > 5) {
    return res.status(400).json({ message: "rating must be between 1 and 5" });
  }

  try {
    await db.query(
      `INSERT INTO product_reviews (user_id, product_id, rating, comment)
       VALUES ($1, $2, $3, $4)`,
      [req.user.id, productId, r, comment || null]
    );
    res.status(201).json({ message: "Review added" });
  } catch (err) {
    console.error("Add review error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

/* ==================================================================
 * 3) Advanced Order History + CSV export
 * =================================================================*/

router.get("/orders/advanced", authMiddleware, async (req, res) => {
  const userId = req.user.id;
  const { status, from, to } = req.query;

  let query = `
    SELECT id, total_amount, status, payment_method, delivery_address, created_at
    FROM orders
    WHERE user_id = $1
  `;
  const params = [userId];
  let idx = 2;

  if (status) {
    query += ` AND status = $${idx++}`;
    params.push(status);
  }
  if (from) {
    query += ` AND created_at >= $${idx++}`;
    params.push(from);
  }
  if (to) {
    query += ` AND created_at <= $${idx++}`;
    params.push(to);
  }

  query += " ORDER BY created_at DESC";

  try {
    const result = await db.query(query, params);
    res.json(result.rows);
  } catch (err) {
    console.error("Advanced orders error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.get("/orders/advanced/export", authMiddleware, async (req, res) => {
  const userId = req.user.id;
  try {
    const result = await db.query(
      `SELECT id, total_amount, status, payment_method, created_at
       FROM orders
       WHERE user_id = $1
       ORDER BY created_at DESC`,
      [userId]
    );

    let csv = "id,total_amount,status,payment_method,created_at\n";
    for (const row of result.rows) {
      csv += `${row.id},${row.total_amount},${row.status},${row.payment_method},${row.created_at.toISOString()}\n`;
    }

    res.header("Content-Type", "text/csv");
    res.attachment("orders.csv");
    res.send(csv);
  } catch (err) {
    console.error("Export orders CSV error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

/* ==================================================================
 * 4) User Profile – default address
 * =================================================================*/

router.get("/me", authMiddleware, async (req, res) => {
  try {
    const result = await db.query(
      "SELECT id, username, default_address, is_admin, created_at FROM users WHERE id = $1",
      [req.user.id]
    );
    if (result.rows.length === 0) {
      return res.status(404).json({ message: "User not found" });
    }
    res.json(result.rows[0]);
  } catch (err) {
    console.error("Get profile error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

router.put("/me/address", authMiddleware, async (req, res) => {
  const { defaultAddress } = req.body || {};
  try {
    await db.query(
      "UPDATE users SET default_address = $1 WHERE id = $2",
      [defaultAddress || null, req.user.id]
    );
    res.json({ message: "Address updated" });
  } catch (err) {
    console.error("Update address error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

/* ==================================================================
 * 14) Admin Dashboard – KPIs + login stats + 12h login trend
 * =================================================================*/

router.get("/admin/metrics", authMiddleware, adminOnly, async (req, res) => {
  try {
    const [
      usersRes,
      ordersRes,
      revenueRes,
      topProductsRes,
      totalLoginsRes,
      activeUsersRes
    ] = await Promise.all([
      db.query("SELECT COUNT(*) AS total_users FROM users"),
      db.query("SELECT COUNT(*) AS total_orders FROM orders"),
      db.query(
        "SELECT COALESCE(SUM(total_amount), 0) AS total_revenue FROM orders"
      ),
      db.query(
        `SELECT p.id,
                p.name,
                SUM(oi.quantity) AS units_sold
         FROM order_items oi
         JOIN products p ON oi.product_id = p.id
         GROUP BY p.id, p.name
         ORDER BY units_sold DESC
         LIMIT 5`
      ),
      // total_logins: every login event ever
      db.query("SELECT COUNT(*) AS total_logins FROM login_events"),
      // active_users_realtime: distinct users who logged in within ACTIVE_WINDOW_MINUTES
      db.query(
        `SELECT COUNT(DISTINCT user_id) AS active_users
         FROM login_events
         WHERE login_at >= now() - INTERVAL '${ACTIVE_WINDOW_MINUTES} minutes'`
      )
    ]);

    res.json({
      total_users: Number(usersRes.rows[0].total_users) || 0,
      total_orders: Number(ordersRes.rows[0].total_orders) || 0,
      total_revenue: Number(revenueRes.rows[0].total_revenue) || 0,
      top_products: topProductsRes.rows || [],
      total_logins: Number(totalLoginsRes.rows[0].total_logins) || 0,
      active_users_realtime:
        Number(activeUsersRes.rows[0].active_users) || 0
    });
  } catch (err) {
    console.error("Admin metrics error:", err);
    res.status(500).json({ message: "Internal server error" });
  }
});

/**
 * 12-hour login trend for charts (both line + bar on frontend)
 * Returns buckets per hour with login_count.
 */
router.get(
  "/admin/login-trend-12h",
  authMiddleware,
  adminOnly,
  async (req, res) => {
    try {
      const result = await db.query(
        `SELECT
           date_trunc('hour', login_at) AS hour_bucket,
           COUNT(*) AS login_count
         FROM login_events
         WHERE login_at >= now() - INTERVAL '12 hours'
         GROUP BY hour_bucket
         ORDER BY hour_bucket`
      );

      const data = result.rows.map((row) => ({
        hour_start: row.hour_bucket,
        // label is ISO string; frontend converts to HH:mm
        label: new Date(row.hour_bucket).toISOString(),
        login_count: Number(row.login_count)
      }));

      res.json(data);
    } catch (err) {
      console.error("Admin login trend (12h) error:", err);
      res.status(500).json({ message: "Internal server error" });
    }
  }
);

module.exports = router;

