const express = require('express');
const mysql = require('mysql2');
const cors = require('cors');

const app = express();
app.use(cors());
app.use(express.json());

const db = mysql.createConnection({
    host: 'localhost',
    user: 'root',
    password: 'rodrigo1234',
    database: 'coworking_reservation'
});

db.connect((err) => {
    if (err) {
        console.error('Error connecting to the database:', err);
        return;
    }
    console.log('Connected to the database.');
});

app.listen(5000, () => {
    console.log('Server running on port 5000');
});

//Ruta para Obtener Espacios Disponibles
app.get('/espacios', (req, res) => {
    const query = 'SELECT * FROM espacios';
    db.query(query, (err, results) => {
        if (err) {
            console.error('Error al obtener espacios:', err);
            res.status(500).json({ error: 'Error al obtener espacios' });
            return;
        }
        res.json(results);
    });
});

//Ruta para Crear una Nueva Reserva
app.post('/reservas', (req, res) => {
    console.log('Solicitud POST recibida en /reservas');
    console.log('Datos recibidos:', req.body);

    const { id_usuario, id_espacio, fecha_reserva, hora_inicio, hora_fin, estado } = req.body;
    const query = 'INSERT INTO reservas (id_usuario, id_espacio, fecha_reserva, hora_inicio, hora_fin, estado) VALUES (?, ?, ?, ?, ?, ?)';

    db.query(query, [id_usuario, id_espacio, fecha_reserva, hora_inicio, hora_fin, estado], (err, result) => {
        if (err) {
            console.error('Error al crear reserva:', err);
            res.status(500).json({ error: 'Error al crear reserva' });
            return;
        }
        res.json({ message: 'Reserva creada exitosamente', id: result.insertId });
    });
});


//Ruta para Obtener Reservas
app.get('/reservas', (req, res) => {
    const query = 'SELECT * FROM reservas';
    db.query(query, (err, results) => {
        if (err) {
            console.error('Error al obtener reservas:', err);
            res.status(500).json({ error: 'Error al obtener reservas' });
            return;
        }
        res.json(results);
    });
});

//Ruta para Actualizar una Reserva
app.put('/reservas/:id', (req, res) => {
    const { id } = req.params;
    const { estado } = req.body;
    const query = 'UPDATE reservas SET estado = ? WHERE id = ?';

    db.query(query, [estado, id], (err, result) => {
        if (err) {
            console.error('Error al actualizar reserva:', err);
            res.status(500).json({ error: 'Error al actualizar reserva' });
            return;
        }
        res.json({ message: 'Reserva actualizada exitosamente' });
    });
});

// Ruta para Eliminar una Reserva
app.delete('/reservas/:id', (req, res) => {
    const { id } = req.params;
    const query = 'DELETE FROM reservas WHERE id = ?';

    db.query(query, [id], (err, result) => {
        if (err) {
            console.error('Error al eliminar reserva:', err);
            res.status(500).json({ error: 'Error al eliminar reserva' });
            return;
        }
        res.json({ message: 'Reserva eliminada exitosamente' });
    });
});
