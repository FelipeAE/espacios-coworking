import React from 'react';
import Header from './components/Header';
import Espacios from './components/Espacios';
import ReservaForm from './components/ReservaForm';
import ListaReservas from './components/ListaReservas';

const App = () => {
    return (
        <div className="App">
            <Header />
            <Espacios />
            <ReservaForm />
            <ListaReservas />
        </div>
    );
};

export default App;
