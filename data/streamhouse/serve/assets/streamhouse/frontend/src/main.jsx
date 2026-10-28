import React,{useState} from 'react';
import {createRoot} from 'react-dom/client';
import App from './App.jsx';
import Login,{SESSION_KEY} from './components/Login.jsx';
import './styles.scss';
function Root(){
  const [user,setUser]=useState(()=>sessionStorage.getItem(SESSION_KEY));
  const signOut=()=>{sessionStorage.removeItem(SESSION_KEY);setUser(null);};
  return user?<App user={user} onSignOut={signOut}/>:<Login onSuccess={setUser}/>;
}
createRoot(document.getElementById('root')).render(<React.StrictMode><Root/></React.StrictMode>);
