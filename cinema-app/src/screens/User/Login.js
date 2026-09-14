import React, { useState, useContext } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import '../../styles/Login.css';

import Apis, { endpoints, authApis } from '../../configs/Apis';
import cookies from 'react-cookies';
import { MyUserContext } from '../../configs/context';

const Login = () => {
    const [user, setUser] = useState({
        username: "",
        password: ""
    });

    const [err, setErr] = useState("");
    const [loading, setLoading] = useState(false);

    const [, dispatch] = useContext(MyUserContext);
    const [q] = useSearchParams();
    const nav = useNavigate();

    const handleChange = (e) => {
        setUser({
            ...user,
            [e.target.id]: e.target.value
        });
    };

    const validate = () => {
        if (!user.username || !user.password) {
            setErr("Vui lòng nhập đầy đủ thông tin!");
            return false;
        }
        setErr("");
        return true;
    };

    const login = async (e) => {
        e.preventDefault();

        if (!validate()) return;

        try {
            setLoading(true);
            let res = await Apis.post(endpoints['login'], user);
            const token = res.data.token || res.data.access || "mock-token-session";
            cookies.save('token', token, { path: '/' });
            localStorage.setItem('access_token', token);

            let userData = res.data.user || { username: user.username, name: user.username };
            try {
                let p = await authApis().get(endpoints['profile']);
                if (p.data) {
                    userData = Array.isArray(p.data) ? (p.data[0] || userData) : p.data;
                }
            } catch (pErr) {
                console.warn("Chưa lấy được profile chi tiết, dùng thông tin đăng nhập:", pErr);
            }

            cookies.save('user', userData, { path: '/' });
            dispatch({
                type: "LOGIN",
                payload: userData
            });
            let next = q.get('next');
            nav(next ? next : '/');

        } catch (ex) {
            console.error(ex);
            setErr("Đăng nhập thất bại! Vui lòng kiểm tra lại tên đăng nhập và mật khẩu.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2 className="login-title">Đăng Nhập</h2>
                <p className="login-subtitle">Chào mừng bạn trở lại với CineBook</p>

                {err && <p style={{ color: 'red' }}>{err}</p>}

                <form className="login-form" onSubmit={login}>
                    
                    <div className="input-group">
                        <label htmlFor="username">Tên đăng nhập</label>
                        <input
                            type="text"
                            id="username"
                            value={user.username}
                            onChange={handleChange}
                            placeholder="Nhập tên đăng nhập..."
                            className="login-input"
                        />
                    </div>

                    <div className="input-group">
                        <label htmlFor="password">Mật khẩu</label>
                        <input
                            type="password"
                            id="password"
                            value={user.password}
                            onChange={handleChange}
                            placeholder="Nhập mật khẩu..."
                            className="login-input"
                        />
                    </div>

                
                    <div className="forgot-password">
                        <a href="#!">Quên mật khẩu?</a>
                    </div>

                
                    <button
                        type="submit"
                        className="btn-submit-login"
                        disabled={loading}
                    >
                        {loading ? "Đang đăng nhập..." : "Đăng Nhập"}
                    </button>
                </form>

                <div className="login-footer">
                    <span>Bạn chưa có tài khoản? </span>
                    <Link to="/register" className="register-link">
                        Đăng ký ngay
                    </Link>
                </div>
            </div>
        </div>
    );
};

export default Login;