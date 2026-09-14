import React, { lazy, Suspense, useReducer } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Header from "./components/Header"; 
import Footer from "./components/Footer";
import ChatWidget from "./components/ChatWidget";
import MySpinner from "./components/MySpinner/MySpinner";
import 'bootstrap/dist/css/bootstrap.min.css';
import { MyUserContext } from "./configs/context";
import MyUserReducer from "./reducers/MyUserReducers";
import cookies from "react-cookies";

// Cơ chế lazy lòa => chỉ hiện những thứ cần thiết
const Home = lazy(() => import("./screens/home/Home"));
const MovieDetails = lazy(() => import("./screens/home/movie_detail"));
const Login = lazy(() => import("./screens/User/Login"));
const Register = lazy(() => import("./screens/User/Register"));
const Ticket = lazy(() => import("./screens/Ticket/Ticket"));
const VNPayReturn = lazy(() => import("./screens/Ticket/VNPayReturn"));
const UserProfile = lazy(() => import("./screens/home/UserProfile"));

const App = () => {
  const [user, dispatch] = useReducer(MyUserReducer, cookies.load('user') || null);
  return (
    <MyUserContext.Provider value={[user, dispatch]}>
      <BrowserRouter>
        <Header />

        <Suspense fallback={
          <div className="d-flex justify-content-center align-items-center" style={{ minHeight: '60vh' }}>
            <MySpinner />
          </div>
        }>
          <Routes>
            <Route path="/" element={<Home />} /> 
            <Route path="/home" element={<Home />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/movies/:movieId" element={<MovieDetails />} />
            <Route path="/lich-su-dat-ve" element={<Ticket />} />
            <Route path="/vnpay-return" element={<VNPayReturn />} />
            <Route path="/profile" element={<UserProfile />} />
          </Routes>
        </Suspense>

        <ChatWidget />
        <Footer />
      </BrowserRouter>
    </MyUserContext.Provider>
  );
};

export default App;