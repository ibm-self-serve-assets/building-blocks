# React Class → Hooks Migration

## Key Transformations

### 1. State Management
```javascript
// Before: Class Component
class UserProfile extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            user: null,
            loading: true
        };
    }
}

// After: Functional Component with Hooks
function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
}
```

### 2. Lifecycle Methods
```javascript
// Before: componentDidMount
componentDidMount() {
    this.fetchUser();
}

// After: useEffect
useEffect(() => {
    fetchUser();
}, []); // Empty array = run once on mount

// Before: componentDidUpdate
componentDidUpdate(prevProps) {
    if (prevProps.userId !== this.props.userId) {
        this.fetchUser();
    }
}

// After: useEffect with dependency
useEffect(() => {
    fetchUser();
}, [userId]); // Run when userId changes

// Before: componentWillUnmount
componentWillUnmount() {
    this.cancelRequest();
}

// After: useEffect cleanup
useEffect(() => {
    return () => {
        cancelRequest();
    };
}, []);
```

### 3. Complete Example
```javascript
// Before: Class Component
class UserProfile extends React.Component {
    constructor(props) {
        super(props);
        this.state = { user: null, loading: true, error: null };
    }
    
    componentDidMount() {
        this.fetchUser();
    }
    
    componentDidUpdate(prevProps) {
        if (prevProps.userId !== this.props.userId) {
            this.fetchUser();
        }
    }
    
    fetchUser() {
        this.setState({ loading: true });
        fetchUserData(this.props.userId)
            .then(user => this.setState({ user, loading: false }))
            .catch(error => this.setState({ error, loading: false }));
    }
    
    render() {
        const { user, loading, error } = this.state;
        if (loading) return <div>Loading...</div>;
        if (error) return <div>Error: {error.message}</div>;
        return <div><h1>{user.name}</h1></div>;
    }
}

// After: Functional Component with Hooks
function UserProfile({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    
    useEffect(() => {
        let cancelled = false;
        
        setLoading(true);
        fetchUserData(userId)
            .then(user => {
                if (!cancelled) {
                    setUser(user);
                    setLoading(false);
                }
            })
            .catch(error => {
                if (!cancelled) {
                    setError(error);
                    setLoading(false);
                }
            });
        
        return () => {
            cancelled = true;
        };
    }, [userId]);
    
    if (loading) return <div>Loading...</div>;
    if (error) return <div>Error: {error.message}</div>;
    return <div><h1>{user.name}</h1></div>;
}
```

## Common Hooks

- **useState**: Manage component state
- **useEffect**: Side effects and lifecycle
- **useContext**: Access context values
- **useCallback**: Memoize callbacks
- **useMemo**: Memoize expensive computations
- **useRef**: Access DOM elements or persist values

## Migration Checklist
- [ ] Convert constructor + state to useState
- [ ] Replace componentDidMount with useEffect
- [ ] Replace componentDidUpdate with useEffect + dependencies
- [ ] Replace componentWillUnmount with useEffect cleanup
- [ ] Remove this.setState calls
- [ ] Remove this.props references
- [ ] Add cleanup for async operations
- [ ] Test component behavior matches original