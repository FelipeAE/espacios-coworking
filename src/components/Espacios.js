import React, { useState, useEffect } from 'react';
import { obtenerEspacios } from '../services/api';

const Espacios = () => {
    const [espacios, setEspacios] = useState([]);

    useEffect(() => {
        obtenerEspacios().then((response) => {
            setEspacios(response.data);
        }).catch((error) => {
            console.error('Error al obtener espacios', error);
        });
    }, []);

    return (
        <div>
            <h2>Espacios Disponibles</h2>
            <ul>
                {espacios.map((espacio) => (
                    <li key={espacio.ID_Espacio}>
                        {espacio.Nombre} - Capacidad: {espacio.Capacidad} - {espacio.Disponibilidad ? 'Disponible' : 'No disponible'}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Espacios;
