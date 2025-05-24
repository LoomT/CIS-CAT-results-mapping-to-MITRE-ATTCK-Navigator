import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Route, Routes } from 'react-router-dom';
import './index.css';
import UserScreen from './UserScreen.jsx';
import HomeScreen from './HomeScreen.jsx';
import AdminLogin from './AdminLogin.jsx';
import AdminOverview from './AdminOverview.jsx';

const [language, setLanguage] = useState('en');
const t = translations[language];

/**
 * Main Component
 * --------------
 * The central component of the application that manages navigation between different
 * screens using internal state.
 */
createRoot(document.getElementById('root')).render(
  <BrowserRouter>
    <Routes>
      <Route index element={<HomeScreen />} />
      <Route path="/manual-conversion" element={<UserScreen />} />
      <Route path="/admin" element={<AdminLogin />} />
      <Route path="/admin/overview" element={<AdminOverview />} />
    </Routes>
  </BrowserRouter>,
);
