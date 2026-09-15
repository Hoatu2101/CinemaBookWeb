import React, { useContext } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "react-bootstrap";
import "../styles/Header.css";
import { MyUserContext } from "../configs/context";
import { formatAvatarUrl, DEFAULT_AVATAR } from "../configs/Apis";

const Header = () => {
    const [user, dispatch] = useContext(MyUserContext);
    const nav = useNavigate(); 

    const handleLogout = () => {
        dispatch({ type: "LOGOUT" });
        nav("/login"); 
    };

    const displayName = user ? (user.username || user.first_name || user.name || "Thành viên") : "";

    return (
        <header className="cinema-header">
            <Link to="/" className="logo-container">
                <h1 className="logo-text">CineBook</h1>
            </Link>

            <div className="nav-menu">
                <Link to="/" className="nav-item nav-item-red">
                    Phim
                </Link>
                <Link to="/lich-su-dat-ve" className="nav-item nav-item-white">
                    Vé của tôi
                </Link>

                {user === null ? (
                    <div className="auth-buttons">
                        <Link to="/login" className="btn-login">Đăng nhập</Link>
                        <Link to="/register" className="btn-register">Đăng ký</Link>
                    </div>
                ) : (
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                        <Link 
                            to="/profile" 
                            style={{ 
                                display: "flex", 
                                alignItems: "center", 
                                gap: "10px", 
                                textDecoration: "none",
                                cursor: "pointer"
                            }}
                            title="Đến Trang cá nhân"
                        >
                            <img
                                src={formatAvatarUrl(user?.avatar)} 
                                width={40}
                                height={40}
                                style={{ 
                                    objectFit: "cover", 
                                    border: "2px solid #e50914",
                                    backgroundColor: "#fff"
                                }}
                                className="rounded-circle"
                                alt="avatar"
                                onError={(e) => {
                                    e.target.onerror = null;
                                    e.target.src = DEFAULT_AVATAR;
                                }}
                            />

                            <span style={{ fontWeight: "500", color: "#fff" }}>
                                Xin chào, {displayName}!
                            </span>
                        </Link>

                        <Link to="/profile" className="nav-item nav-item-white" style={{ fontSize: "14px", padding: "4px 8px" }}>
                            Trang cá nhân
                        </Link>

                        <Button
                            variant="danger"
                            size="sm"
                            style={{
                                backgroundColor: "#e50914",
                                borderColor: "#e50914",
                                fontWeight: "600",
                                padding: "6px 16px",
                                borderRadius: "20px",
                                boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
                                transition: "all 0.3s ease"
                            }}
                            onClick={handleLogout}
                        >
                            Đăng xuất
                        </Button>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;