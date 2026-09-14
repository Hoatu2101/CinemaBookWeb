import React, { useState, useEffect, useContext, useRef } from "react";
import { useNavigate } from "react-router-dom";
import cookies from "react-cookies";
import { endpoints, authApis } from "../../configs/Apis";
import { MyUserContext } from "../../configs/context";
import MySpinner from "../../components/MySpinner/MySpinner";
import "../../styles/UserProfile.css";

const UserProfileScreen = () => {
    const [user, dispatch] = useContext(MyUserContext);
    const nav = useNavigate();

    const [activeTab, setActiveTab] = useState("info");

    // Profile state
    const [formData, setFormData] = useState({
        name: "",
        email: "",
        number_phone: "",
        username: ""
    });

    // Avatar update state
    const [avatarFile, setAvatarFile] = useState(null);
    const [avatarPreview, setAvatarPreview] = useState("");
    const fileInputRef = useRef(null);

    // Password change state
    const [pwdData, setPwdData] = useState({
        current_password: "",
        new_password: "",
        confirm_password: ""
    });

    const [showCurrentPwd, setShowCurrentPwd] = useState(false);
    const [showNewPwd, setShowNewPwd] = useState(false);
    const [showConfirmPwd, setShowConfirmPwd] = useState(false);

    // UI Feedback states
    const [loading, setLoading] = useState(false);
    const [successMsg, setSuccessMsg] = useState("");
    const [errorMsg, setErrorMsg] = useState("");

    useEffect(() => {
        if (!user) {
            nav("/login?next=/profile");
            return;
        }

        // Initialize form data from context user
        setFormData({
            name: user.name || user.first_name || "",
            email: user.email || "",
            number_phone: user.number_phone || "",
            username: user.username || ""
        });

        if (user.avatar) {
            setAvatarPreview(user.avatar);
        }

        // Fetch fresh details from backend
        fetchFreshProfile();
    }, [user, nav]);

    const fetchFreshProfile = async () => {
        try {
            const res = await authApis().get(endpoints["current_user"]);
            if (res.data) {
                const freshUser = res.data;
                setFormData({
                    name: freshUser.name || freshUser.first_name || "",
                    email: freshUser.email || "",
                    number_phone: freshUser.number_phone || "",
                    username: freshUser.username || ""
                });
                if (freshUser.avatar) {
                    setAvatarPreview(freshUser.avatar);
                }
            }
        } catch (err) {
            console.warn("Could not fetch fresh user profile info:", err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setFormData((prev) => ({ ...prev, [name]: value }));
    };

    const handlePwdChange = (e) => {
        const { name, value } = e.target;
        setPwdData((prev) => ({ ...prev, [name]: value }));
    };

    const clearAlerts = () => {
        setSuccessMsg("");
        setErrorMsg("");
    };

    // Save Personal Information
    const handleSaveInfo = async (e) => {
        e.preventDefault();
        clearAlerts();

        if (!formData.name.trim()) {
            setErrorMsg("Họ và tên không được để trống!");
            return;
        }

        try {
            setLoading(true);
            const reqBody = new FormData();
            reqBody.append("name", formData.name.trim());
            reqBody.append("email", formData.email.trim());
            reqBody.append("number_phone", formData.number_phone.trim());

            const res = await authApis().patch(endpoints["update_profile"], reqBody);

            if (res.data && res.data.user) {
                const updatedUser = { ...user, ...res.data.user };
                cookies.save("user", updatedUser, { path: "/" });
                dispatch({ type: "LOGIN", payload: updatedUser });
                setSuccessMsg("Cập nhật thông tin cá nhân thành công!");
            }
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.error || "Cập nhật thông tin thất bại!";
            setErrorMsg(msg);
        } finally {
            setLoading(false);
        }
    };

    // Handle File Selection for Avatar
    const handleAvatarSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            if (!file.type.startsWith("image/")) {
                setErrorMsg("Vui lòng chọn tệp hình ảnh hợp lệ!");
                return;
            }
            clearAlerts();
            setAvatarFile(file);
            setAvatarPreview(URL.createObjectURL(file));
        }
    };

    // Save Avatar
    const handleUploadAvatar = async () => {
        if (!avatarFile) {
            setErrorMsg("Vui lòng chọn ảnh trước khi tải lên!");
            return;
        }

        clearAlerts();

        try {
            setLoading(true);
            const reqBody = new FormData();
            reqBody.append("avatar", avatarFile);

            const res = await authApis().patch(endpoints["update_profile"], reqBody, {
                headers: { "Content-Type": "multipart/form-data" }
            });

            if (res.data && res.data.user) {
                const updatedUser = { ...user, ...res.data.user };
                cookies.save("user", updatedUser, { path: "/" });
                dispatch({ type: "LOGIN", payload: updatedUser });
                setAvatarFile(null);
                setSuccessMsg("Đã cập nhật ảnh đại diện thành công!");
            }
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.error || "Không thể tải lên ảnh đại diện!";
            setErrorMsg(msg);
        } finally {
            setLoading(false);
        }
    };

    // Save New Password
    const handleChangePasswordSubmit = async (e) => {
        e.preventDefault();
        clearAlerts();

        if (!pwdData.current_password || !pwdData.new_password || !pwdData.confirm_password) {
            setErrorMsg("Vui lòng nhập đầy đủ thông tin mật khẩu!");
            return;
        }

        if (pwdData.new_password.length < 6) {
            setErrorMsg("Mật khẩu mới phải có ít nhất 6 ký tự!");
            return;
        }

        if (pwdData.new_password !== pwdData.confirm_password) {
            setErrorMsg("Mật khẩu mới và mật khẩu xác nhận không trùng khớp!");
            return;
        }

        try {
            setLoading(true);
            const res = await authApis().post(endpoints["change_password"], pwdData);

            if (res.data && res.data.success) {
                setSuccessMsg("Đổi mật khẩu thành công!");
                setPwdData({ current_password: "", new_password: "", confirm_password: "" });
            }
        } catch (err) {
            console.error(err);
            const msg = err.response?.data?.error || "Đổi mật khẩu thất bại. Vui lòng kiểm tra lại mật khẩu hiện tại!";
            setErrorMsg(msg);
        } finally {
            setLoading(false);
        }
    };

    const userDisplayName = user?.username || user?.name || user?.first_name || "Thành viên";
    const userAvatarUrl = avatarPreview || user?.avatar || "https://cdn-icons-png.flaticon.com/512/149/149071.png";
    const roleLabel = user?.role === "ROLE_ADMIN" ? "Quản trị viên" : user?.role === "ROLE_STAFF" ? "Nhân viên" : "Khách hàng";

    return (
        <div className="profile-container">
            <div className="profile-content-wrapper">
                {/* Header Card */}
                <div className="profile-header-card">
                    <div className="header-avatar-wrapper">
                        <img src={userAvatarUrl} alt="Avatar" className="header-avatar-img" />
                        <div 
                            className="avatar-badge" 
                            title="Đổi ảnh đại diện"
                            onClick={() => {
                                setActiveTab("avatar");
                                setTimeout(() => fileInputRef.current?.click(), 100);
                            }}
                        >
                            Sửa
                        </div>
                    </div>
                    <div className="profile-header-info">
                        <h2 className="profile-user-name">
                            {userDisplayName}
                            <span className="role-tag">{roleLabel}</span>
                        </h2>
                        <div className="profile-user-meta">
                            <span className="meta-item">@{user?.username}</span>
                            {formData.email && <span className="meta-item">{formData.email}</span>}
                            {formData.number_phone && <span className="meta-item">{formData.number_phone}</span>}
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="profile-tabs">
                    <button
                        className={`tab-btn ${activeTab === "info" ? "active" : ""}`}
                        onClick={() => { setActiveTab("info"); clearAlerts(); }}
                    >
                        Thông Tin Cá Nhân
                    </button>
                    <button
                        className={`tab-btn ${activeTab === "avatar" ? "active" : ""}`}
                        onClick={() => { setActiveTab("avatar"); clearAlerts(); }}
                    >
                        Đổi Ảnh Đại Diện
                    </button>
                    <button
                        className={`tab-btn ${activeTab === "password" ? "active" : ""}`}
                        onClick={() => { setActiveTab("password"); clearAlerts(); }}
                    >
                        Đổi Mật Khẩu
                    </button>
                </div>

                {/* Feedback Alerts */}
                {successMsg && <div className="alert-box alert-success">{successMsg}</div>}
                {errorMsg && <div className="alert-box alert-error">{errorMsg}</div>}

                {/* Body Card */}
                <div className="profile-body-card">
                    {/* TAB 1: Personal Info */}
                    {activeTab === "info" && (
                        <form onSubmit={handleSaveInfo}>
                            <h3 className="section-title">Thông Tin Cá Nhân</h3>
                            <p className="section-desc">Cập nhật họ tên và thông tin liên lạc của bạn trên CineBook</p>

                            <div className="profile-form-grid">
                                <div className="profile-form-group">
                                    <label>Tên đăng nhập (Username)</label>
                                    <input
                                        type="text"
                                        className="profile-input"
                                        value={formData.username}
                                        disabled
                                    />
                                </div>

                                <div className="profile-form-group">
                                    <label>Họ và tên</label>
                                    <input
                                        type="text"
                                        name="name"
                                        className="profile-input"
                                        value={formData.name}
                                        onChange={handleInputChange}
                                        placeholder="Nhập họ tên của bạn..."
                                        required
                                    />
                                </div>

                                <div className="profile-form-group">
                                    <label>Địa chỉ Email</label>
                                    <input
                                        type="email"
                                        name="email"
                                        className="profile-input"
                                        value={formData.email}
                                        onChange={handleInputChange}
                                        placeholder="Nhập email..."
                                    />
                                </div>

                                <div className="profile-form-group">
                                    <label>Số điện thoại</label>
                                    <input
                                        type="tel"
                                        name="number_phone"
                                        className="profile-input"
                                        value={formData.number_phone}
                                        onChange={handleInputChange}
                                        placeholder="Nhập số điện thoại..."
                                    />
                                </div>
                            </div>

                            <button type="submit" className="btn-save-profile" disabled={loading}>
                                {loading ? <MySpinner /> : "Lưu Thay Đổi"}
                            </button>
                        </form>
                    )}

                    {/* TAB 2: Edit Avatar */}
                    {activeTab === "avatar" && (
                        <div className="avatar-upload-container">
                            <h3 className="section-title">Đổi Ảnh Đại Diện</h3>
                            <p className="section-desc">Chọn hình ảnh mới từ máy tính của bạn (hỗ trợ JPG, PNG, WEBP)</p>

                            <div 
                                className="avatar-preview-box" 
                                onClick={() => fileInputRef.current?.click()}
                            >
                                <img src={userAvatarUrl} alt="Avatar Preview" className="avatar-preview-img" />
                                <div className="avatar-upload-overlay">
                                    <span>Click chọn ảnh</span>
                                </div>
                            </div>

                            <input
                                type="file"
                                ref={fileInputRef}
                                accept="image/*"
                                style={{ display: "none" }}
                                onChange={handleAvatarSelect}
                            />

                            <div style={{ display: "flex", gap: "12px", alignItems: "center" }}>
                                <button
                                    type="button"
                                    className="btn-save-profile"
                                    style={{ background: "#2d3348", color: "#fff" }}
                                    onClick={() => fileInputRef.current?.click()}
                                >
                                    Chọn Ảnh Từ Máy Tính
                                </button>

                                {avatarFile && (
                                    <button
                                        type="button"
                                        className="btn-save-profile"
                                        onClick={handleUploadAvatar}
                                        disabled={loading}
                                    >
                                        {loading ? <MySpinner /> : "Tải Ảnh Lên"}
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* TAB 3: Change Password */}
                    {activeTab === "password" && (
                        <form onSubmit={handleChangePasswordSubmit}>
                            <h3 className="section-title">Đổi Mật Khẩu</h3>
                            <p className="section-desc">Đảm bảo an toàn cho tài khoản bằng mật khẩu mạnh</p>

                            <div className="profile-form-grid">
                                <div className="profile-form-group form-group-full">
                                    <label>Mật khẩu hiện tại</label>
                                    <div className="profile-input-wrapper">
                                        <input
                                            type={showCurrentPwd ? "text" : "password"}
                                            name="current_password"
                                            className="profile-input"
                                            value={pwdData.current_password}
                                            onChange={handlePwdChange}
                                            placeholder="Nhập mật khẩu hiện tại..."
                                            required
                                        />
                                        <button
                                            type="button"
                                            className="toggle-pwd-btn"
                                            onClick={() => setShowCurrentPwd(!showCurrentPwd)}
                                        >
                                            {showCurrentPwd ? "Ẩn" : "Hiện"}
                                        </button>
                                    </div>
                                </div>

                                <div className="profile-form-group">
                                    <label>Mật khẩu mới</label>
                                    <div className="profile-input-wrapper">
                                        <input
                                            type={showNewPwd ? "text" : "password"}
                                            name="new_password"
                                            className="profile-input"
                                            value={pwdData.new_password}
                                            onChange={handlePwdChange}
                                            placeholder="Tối thiểu 6 ký tự..."
                                            required
                                        />
                                        <button
                                            type="button"
                                            className="toggle-pwd-btn"
                                            onClick={() => setShowNewPwd(!showNewPwd)}
                                        >
                                            {showNewPwd ? "Ẩn" : "Hiện"}
                                        </button>
                                    </div>
                                </div>

                                <div className="profile-form-group">
                                    <label>Xác nhận mật khẩu mới</label>
                                    <div className="profile-input-wrapper">
                                        <input
                                            type={showConfirmPwd ? "text" : "password"}
                                            name="confirm_password"
                                            className="profile-input"
                                            value={pwdData.confirm_password}
                                            onChange={handlePwdChange}
                                            placeholder="Nhập lại mật khẩu mới..."
                                            required
                                        />
                                        <button
                                            type="button"
                                            className="toggle-pwd-btn"
                                            onClick={() => setShowConfirmPwd(!showConfirmPwd)}
                                        >
                                            {showConfirmPwd ? "Ẩn" : "Hiện"}
                                        </button>
                                    </div>
                                </div>
                            </div>

                            <button type="submit" className="btn-save-profile" disabled={loading}>
                                {loading ? <MySpinner /> : "Đổi Mật Khẩu"}
                            </button>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default UserProfileScreen;
