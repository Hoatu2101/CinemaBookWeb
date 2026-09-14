import axios from "axios";
import cookies from "react-cookies";

const BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000/api/";

export const endpoints = {
    'movies': "/movies/",
    'detail_movie': (id) => `/movies/${id}/`,
    'categories': "/categories/",
    'formats': "/movie-formats/",
    'cinemas': "/cinemas/",
    'register': "/users/",
    'login': "/login/",
    'profile': "/profiles/",
    'current_user': "/profiles/current/",
    'update_profile': "/profiles/update-profile/",
    'change_password': "/profiles/change-password/",
    'movie_showtimes': (movieId) => `/showtimes/?movie_id=${movieId}`,
    'seats': (showtimeId) => `/showtimes/${showtimeId}/seats/`,
    'booking': '/bookings/',
    'my_bookings': '/bookings/',
    'tickets': '/tickets/',
    'type_tickets': '/type-tickets/'
};

export const authApis = () => {
    const token = cookies.load("token") || localStorage.getItem("access_token");

    return axios.create({
        baseURL: BASE_URL,
        headers: token
            ? {
                  Authorization: `Bearer ${token}`,
              }
            : {},
    });
};

export default axios.create({
    baseURL: BASE_URL,
});