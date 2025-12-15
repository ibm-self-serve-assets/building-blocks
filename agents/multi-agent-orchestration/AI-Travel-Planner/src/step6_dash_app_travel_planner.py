import dash
from dash import Dash, html

app = Dash(
    __name__,
    external_scripts=[],
    external_stylesheets=[]
)

# ---------------------------------------------------------
# Custom HTML Template (Travel Planner)
# ---------------------------------------------------------
app.index_string = """
<!DOCTYPE html>
<html lang="en">
<head>
    {%metas%}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Travel Planner</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        
        .header {
            background: rgba(255, 255, 255, 0.95);
            padding: 20px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        .header h1 {
            margin: 0;
            color: #333;
            font-size: 2.5em;
            font-weight: 300;
        }
        
        .header p {
            margin: 10px 0 0 0;
            color: #666;
            font-size: 1.1em;
        }
        
        .container {
            flex: 1;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .card {
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
            width: 100%;
            max-width: 1200px;
            height: 600px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #444;
            text-align: center;
        }

        #root {
            width: 100% !important;
            height: 100% !important;
            display: flex !important;
            flex-direction: column !important;
        }

        #root > * {
            width: 100% !important;
            height: 100% !important;
            margin: 0 !important;
            padding: 0 !important;
        }
        
        .footer {
            background: rgba(255, 255, 255, 0.9);
            padding: 15px;
            text-align: center;
            color: #666;
            font-size: 0.9em;
        }
        
        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100%;
            flex-direction: column;
        }
        
        .spinner {
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .loading-text {
            color: #666;
            font-size: 1.1em;
        }
    </style>
    {%css%}
</head>
<body>
    {%app_entry%}

    <div class="header">
        <h1>🧳 Travel Planner</h1>
        <p>Your Personalized Travel Assistant - Powered by AI</p>
    </div>
    
    <div class="container">
        <div class="card">
            <div id="root">
                <div>
                    <h2>Welcome</h2>
                    <p>Click the chat widget at the bottom right corner to start planning your travel!</p>
                </div>
            </div>
        </div>
    </div>
    
    <div class="footer">
        <p>Powered by IBM WatsonX Orchestrate | Start planning your next adventure!</p>
    </div>

<!-- Start: Replace this script section with your WXO Travel Planner information.  -->
    <script>
      window.wxOConfiguration = {
        orchestrationID: "1b3c867ca6584d63860ce3566176953f_aed25cef-6a4a-4ce2-b63f-ce59843bd2f8",
        hostURL: "https://us-south.watson-orchestrate.cloud.ibm.com",
        rootElementID: "root",
        deploymentPlatform: "ibmcloud",
        crn: "crn:v1:bluemix:public:watsonx-orchestrate:us-south:a/1b3c867ca6584d63860ce3566176953f:aed25cef-6a4a-4ce2-b63f-ce59843bd2f8::",
        chatOptions: {
            agentId: "f1254898-dfe6-43d5-a7c1-908005521305", 
        }
      };
      setTimeout(function () {
        const script = document.createElement('script');
        script.src = `${window.wxOConfiguration.hostURL}/wxochat/wxoLoader.js?embed=true`;
        script.addEventListener('load', function () {
            wxoLoader.init();
        });
        document.head.appendChild(script);
      }, 0);                     
    </script>
<!-- End: Replace this script section with your WXO Travel Planner information -->

    {%config%}
    {%scripts%}
    {%renderer%}
</body>
</html>
"""

# Dash Layout (minimal, since most content is in HTML)
app.layout = html.Div(id="wxo")

# Run the server
if __name__ == "__main__":
    app.run(debug=True, port=8050)
