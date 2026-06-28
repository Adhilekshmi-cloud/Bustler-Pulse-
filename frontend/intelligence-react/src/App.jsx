import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import ProtectedRoute from './components/ProtectedRoute';
import { SidebarProvider } from './context/SidebarContext';
import Login from './pages/Login';
import Landing from './pages/Landing';
import Intelligence from './pages/Intelligence';
import Health from './pages/Health';
import Reports from './pages/Reports';
import Heatmap from './pages/Heatmap';
import Agents from './pages/Agents';

function App() {
  return (
    <BrowserRouter>
      <SidebarProvider>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />

          {/* Protected routes */}
          <Route path="/intelligence" element={
            <ProtectedRoute><Intelligence /></ProtectedRoute>
          } />
          <Route path="/health" element={
            <ProtectedRoute><Health /></ProtectedRoute>
          } />
          <Route path="/reports" element={
            <ProtectedRoute><Reports /></ProtectedRoute>
          } />
          <Route path="/heatmap" element={
            <ProtectedRoute><Heatmap /></ProtectedRoute>
          } />
          <Route path="/agents" element={
            <ProtectedRoute><Agents /></ProtectedRoute>
          } />

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </SidebarProvider>
    </BrowserRouter>
  );
}

export default App;