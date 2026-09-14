import cookies from 'react-cookies';

const MyUserReducer = (current, action) => {
    switch (action.type) {
        case "LOGIN":
            cookies.save('user', action.payload, { path: '/' });
            return action.payload;
        case "LOGOUT":
            cookies.remove('token', { path: '/' });
            cookies.remove('user', { path: '/' });
            localStorage.removeItem('access_token');
            localStorage.removeItem('user');
            return null;
        default:
            return current;
    }
};

export default MyUserReducer;