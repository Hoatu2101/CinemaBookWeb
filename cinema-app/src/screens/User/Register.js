import { useRef, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import MySpinner from "../../components/MySpinner/MySpinner";
import Apis, { endpoints } from "../../configs/Apis";
import "../../styles/Register.css";

const Register = () => {
    // Định nghĩa chuẩn theo tên các cột trong database của bạn
    const userInfo = [
        { field: "name", label: "Họ và tên", type: "text", placeholder: "VD: Nguyễn Văn A" },
        { field: "email", label: "Địa chỉ Email (nhận vé xem phim)", type: "email", placeholder: "VD: emailcuaban@gmail.com" },
        { field: "number_phone", label: "Số điện thoại", type: "tel", placeholder: "090xxxxxxx" },
        { field: "username", label: "Tên đăng nhập (Username)", type: "text", placeholder: "Từ 5-20 ký tự..." },
        { field: "password", label: "Mật khẩu", type: "password", placeholder: "Tối thiểu 6 ký tự gồm chữ và số..." },
        { field: "confirm", label: "Xác nhận mật khẩu", type: "password", placeholder: "Nhập lại mật khẩu..." }
    ];

    const [user, setUser] = useState({
        name: "",
        email: "",
        number_phone: "",
        username: "",
        password: "",
        confirm: ""
    });
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);
    const avatar = useRef();
    const nav = useNavigate();

    const changeInput = (field, value) => {
        setUser({ ...user, [field]: value });
        if (errors[field]) {
            setErrors({ ...errors, [field]: "" });
        }
    };

    const validateForm = () => {
        let newErrors = {};
        const nameRegex = /^[a-zA-ZÀÁÂÃÈÉÊÌÍÒÓÔÕÙÚĂĐĨŨƠàáâãèéêìíòóôõùúăđĩũơƯĂÂÊÔƠỨỪỬỮỰẤẦẨẪẬẮẰẲẴẶẸẺẼỀỀỂưăâêôơứừửữựấẩẫậắằẳẵặẹẻẽềềểỄỆỈỊỌỎỐỒỔỖỘỚỜỞỠỢỤỦỨỪỬỮỰÝỲỶỸÝỳỷỹ\s]+$/;
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        const phoneRegex = /^[0-9]{10}$/;
        const usernameRegex = /^[a-zA-Z0-9]{5,20}$/;
        const passwordRegex = /^(?=.*[A-Za-z])(?=.*\d).{6,}$/;

        if (!user.name.trim()) {
            newErrors.name = "Họ và tên không được để trống";
        } else if (!nameRegex.test(user.name)) {
            newErrors.name = "Họ và tên không được chứa số hoặc ký tự đặc biệt";
        }

        if (!user.email.trim()) {
            newErrors.email = "Email không được để trống";
        } else if (!emailRegex.test(user.email)) {
            newErrors.email = "Định dạng email không hợp lệ";
        }

        if (!user.number_phone.trim()) {
            newErrors.number_phone = "Số điện thoại không được để trống";
        } else if (!phoneRegex.test(user.number_phone)) {
            newErrors.number_phone = "Số điện thoại phải gồm đúng 10 chữ số";
        }

        if (!user.username.trim()) {
            newErrors.username = "Tên đăng nhập không được để trống";
        } else if (!usernameRegex.test(user.username)) {
            newErrors.username = "Tên đăng nhập từ 5-20 ký tự, viết liền không dấu, không chứa ký tự đặc biệt";
        }

        if (!user.password) {
            newErrors.password = "Mật khẩu không được để trống";
        } else if (!passwordRegex.test(user.password)) {
            newErrors.password = "Mật khẩu tối thiểu 6 ký tự, bao gồm cả chữ cái và số";
        }

        if (user.password !== user.confirm) {
            newErrors.confirm = "Mật khẩu xác nhận không khớp";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const register = async (e) => {
        e.preventDefault();

        if (validateForm()) {
            let form = new FormData();

            // Đóng gói dữ liệu chuẩn tên key gửi lên Spring Boot backend
            for (var key of Object.keys(user)) {
                if (key !== "confirm") {
                    form.append(key, user[key].trim());
                }
            }

            // Đóng gói key 'avatar' trùng với tên cột lưu ảnh trong database của bạn
            if (avatar.current && avatar.current.files.length > 0) {
                form.append("avatar", avatar.current.files[0]);
            }

            try {
                setLoading(true);
                const res = await Apis.post(endpoints["register"], form, {
                    headers: {
                        "Content-Type": "multipart/form-data"
                    }
                });
                if (res.status === 201 || res.status === 200) {
                    nav("/login");
                }
            } catch (ex) {
                console.error("Lỗi đăng ký:", ex);
                const errMsg = ex.response?.data?.error || ex.response?.data?.message || "Đăng ký thất bại! Vui lòng kiểm tra lại thông tin.";
                alert(errMsg);
            } finally {
                setLoading(false);
            }
        }
    };

    return (
        <div className="register-container">
            <div className="register-box">
                <h2 className="register-title">Đăng Ký Tài Khoản</h2>
                <p className="register-subtitle">Trở thành thành viên của CineBook ngay hôm nay</p>

                <form className="register-form" onSubmit={register}>
                    {userInfo.map((u) => (
                        <div className="input-group" key={u.field}>
                            <label htmlFor={u.field}>{u.label}</label>
                            <input
                                type={u.type}
                                id={u.field}
                                value={user[u.field] || ""}
                                onChange={(e) => changeInput(u.field, e.target.value)}
                                placeholder={u.placeholder}
                                className={`register-input ${errors[u.field] ? "input-error" : ""}`}
                                disabled={loading}
                            />
                            {errors[u.field] && <span className="error-text">{errors[u.field]}</span>}
                        </div>
                    ))}

                    <div className="input-group">
                        <label>Ảnh đại diện (Avatar) - <small style={{ color: "#888" }}>Không bắt buộc</small></label>
                        <div className="file-upload-wrapper">
                            <input
                                type="file"
                                id="file"
                                accept="image/*"
                                ref={avatar}
                                className="file-input-hidden"
                                disabled={loading}
                            />
                            <label htmlFor="file" className="file-upload-btn">
                                <span>📁 Chọn ảnh từ máy tính</span>
                            </label>
                        </div>
                    </div>

                    <div className="form-submit-wrapper" style={{ marginTop: '20px', textAlign: 'center' }}>
                        {loading === true ? (
                            <MySpinner />
                        ) : (
                            <button type="submit" className="btn-submit-register">
                                Đăng Ký Ngay
                            </button>
                        )}
                    </div>
                </form>

                <div className="register-footer">
                    <span>Bạn đã có tài khoản? </span>
                    <Link to="/login" className="login-link">Đăng nhập</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;