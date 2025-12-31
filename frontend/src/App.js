import './App.css';
import DraftPost from './components/DraftPost';
import Login from './components/Login';
import Register from './components/Register';  // ADD THIS LINE
import CatProfile from './components/CatProfile';
import CatScroll from './components/CatScroll'
import NavigationButtons from './components/NavigateButtons';

import {
  BrowserRouter as Router,
  Routes,
  Route,
} from "react-router-dom";

import React, { useState, useEffect } from 'react';

function App() {

  const [username, setUsername] = useState(null);

  async function getUsername() {
    const response = await fetch(`${process.env.REACT_APP_BACKEND_HOST}/users/whoami`, {
      method: 'GET',
      credentials: 'include',
    });
    const resJson = await response.json();
    if (resJson !== null)
      setUsername(resJson.username);
  };

  useEffect(() => {
    getUsername()
  }, []);

  return (
    <Router>
        <div className='header'>
          <h3>marleydacat.site</h3>
        </div>
        <Routes>
          <Route path="/" element={<CatScroll />} />
          <Route path="/login" element={<Login setUsernameFunc={setUsername}/>} />
          <Route path="/register" element={<Register />} />  {/* ADD THIS LINE */}
          <Route path="/post" element={<DraftPost />} />
          <Route path="/scroll" element={<CatScroll />} />
          <Route path="/profile/:username" element={<CatProfile />} />
        </Routes>
        <NavigationButtons username={username} />
    </Router>
  );
}

export default App;