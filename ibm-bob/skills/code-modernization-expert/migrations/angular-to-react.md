# Angular.js → React Migration

## Migration Strategy

Use **Strangler Fig Pattern** - gradually replace Angular.js components with React components.

## Key Differences

| Angular.js | React |
|------------|-------|
| Two-way binding | One-way data flow |
| Controllers | Components |
| $scope | Props & State |
| Directives | Components/Hooks |
| Services | Context/Hooks |
| Templates | JSX |

## Migration Steps

### 1. Set Up React Alongside Angular
```javascript
// Add React to existing Angular app
import React from 'react';
import ReactDOM from 'react-dom';

// Create adapter directive
angular.module('app').directive('reactComponent', function() {
    return {
        restrict: 'E',
        scope: { props: '=' },
        link: function(scope, element) {
            ReactDOM.render(
                React.createElement(MyReactComponent, scope.props),
                element[0]
            );
            scope.$on('$destroy', () => {
                ReactDOM.unmountComponentAtNode(element[0]);
            });
        }
    };
});
```

### 2. Convert Controllers to Components
```javascript
// Before: Angular.js Controller
app.controller('UserController', function($scope, UserService) {
    $scope.user = null;
    $scope.loading = true;
    
    UserService.getUser($scope.userId).then(function(user) {
        $scope.user = user;
        $scope.loading = false;
    });
});

// After: React Component
function UserComponent({ userId }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        UserService.getUser(userId).then(user => {
            setUser(user);
            setLoading(false);
        });
    }, [userId]);
    
    if (loading) return <div>Loading...</div>;
    return <div>{user.name}</div>;
}
```

### 3. Replace Services with Hooks/Context
```javascript
// Before: Angular Service
app.service('UserService', function($http) {
    this.getUser = function(id) {
        return $http.get('/api/users/' + id);
    };
});

// After: React Hook
function useUser(userId) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    
    useEffect(() => {
        fetch(`/api/users/${userId}`)
            .then(res => res.json())
            .then(setUser)
            .finally(() => setLoading(false));
    }, [userId]);
    
    return { user, loading };
}
```

### 4. Convert Templates to JSX
```javascript
// Before: Angular Template
<div ng-controller="UserController">
    <h1>{{user.name}}</h1>
    <p ng-if="loading">Loading...</p>
    <ul>
        <li ng-repeat="item in items">{{item.name}}</li>
    </ul>
</div>

// After: React JSX
function UserView({ userId }) {
    const { user, loading } = useUser(userId);
    
    return (
        <div>
            <h1>{user?.name}</h1>
            {loading && <p>Loading...</p>}
            <ul>
                {items.map(item => (
                    <li key={item.id}>{item.name}</li>
                ))}
            </ul>
        </div>
    );
}
```

## Migration Checklist
- [ ] Set up React build pipeline
- [ ] Create Angular-React adapter
- [ ] Identify components to migrate (start with leaf components)
- [ ] Convert controllers to functional components
- [ ] Replace $scope with props/state
- [ ] Convert services to hooks or context
- [ ] Replace templates with JSX
- [ ] Update routing (Angular router → React Router)
- [ ] Migrate state management (if using)
- [ ] Remove Angular.js when 100% migrated