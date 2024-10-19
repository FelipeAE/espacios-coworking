import React, { useState, useEffect } from 'react';
import { obtenerReservas } from '../services/api';

const ListaReservas = () => {
    const [reservas, setReservas] = useState([]);

    useEffect(() => {
        obtenerReservas().then((response) => {
            setReservas(response.data);
        }).catch((error) => {
            console.error('Error al obtener reservas', error);
        });
    }, []);

    return (
        <div>
            <h2>Reservas Actuales</h2>
            <ul>
                {reservas.map((reserva) => (
                    <li key={reserva.ID_Reserva}>
                        {`Usuario: ${reserva.ID_Usuario} - Espacio: ${reserva.ID_Espacio} - Fecha: ${reserva.Fecha_Reserva} - Estado: ${reserva.Estado}`}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ListaReservas;
