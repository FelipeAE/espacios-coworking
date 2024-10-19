import React, { useState } from 'react';
import { crearReserva } from '../services/api';

const ReservaForm = () => {
    const [reserva, setReserva] = useState({
        ID_Usuario: '',
        ID_Espacio: '',
        Fecha_Reserva: '',
        Hora_Inicio: '',
        Hora_Fin: '',
        Estado: 'Pendiente',
    });

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setReserva({ ...reserva, [name]: value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        crearReserva(reserva)
            .then((response) => {
                alert('Reserva creada con éxito');
                setReserva({
                    ID_Usuario: '',
                    ID_Espacio: '',
                    Fecha_Reserva: '',
                    Hora_Inicio: '',
                    Hora_Fin: '',
                    Estado: 'Pendiente',
                });
            })
            .catch((error) => {
                console.error('Error al crear la reserva', error);
            });
    };

    return (
        <form onSubmit={handleSubmit}>
            <h2>Crear Reserva</h2>
            <label>Usuario ID:</label>
            <input type="text" name="ID_Usuario" value={reserva.ID_Usuario} onChange={handleInputChange} required />
            <label>Espacio ID:</label>
            <input type="text" name="ID_Espacio" value={reserva.ID_Espacio} onChange={handleInputChange} required />
            <label>Fecha Reserva:</label>
            <input type="date" name="Fecha_Reserva" value={reserva.Fecha_Reserva} onChange={handleInputChange} required />
            <label>Hora Inicio:</label>
            <input type="time" name="Hora_Inicio" value={reserva.Hora_Inicio} onChange={handleInputChange} required />
            <label>Hora Fin:</label>
            <input type="time" name="Hora_Fin" value={reserva.Hora_Fin} onChange={handleInputChange} required />
            <button type="submit">Crear Reserva</button>
        </form>
    );
};

export default ReservaForm;
