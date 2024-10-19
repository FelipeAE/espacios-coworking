import axios from 'axios';

const API_URL = 'http://localhost:3000'; // Cambia esto según tu servidor backend

// Obtenemos todas las reservas
export const obtenerReservas = () => {
    return axios.get(`${API_URL}/reservas`);
};

// Obtenemos todos los espacios
export const obtenerEspacios = () => {
    return axios.get(`${API_URL}/espacios`);
};

// Crear una nueva reserva
export const crearReserva = (reserva) => {
    return axios.post(`${API_URL}/reservas`, reserva);
};
