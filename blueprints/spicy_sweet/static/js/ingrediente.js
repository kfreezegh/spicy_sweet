// AGREGAR REGISTRO
$(document).ready(function () {
  $('#btnAgregarRegistro').click(function () {
    $('#modalAgregarRegistro').modal('show');
  });
});
function guardarAñadirRegistro() {
  var nombre = $('#nombre').val();
  var precio = $('#precio').val();
  var descripcion = $('#descripcion').val();
  $.ajax({
    url: '/ingredientes',
    method: 'POST',
    data: {
      nombre: nombre,
      precio: precio,
      descripcion: descripcion
    },
    success: function (response) {
      console.log('Registro guardado correctamente');
      location.reload();
      alert('¡Registro guardado correctamente!');
    },
    error: function (xhr, status, error) {
      console.error('Error al guardar el registro:', error);
      alert('¡Error al guardar el registro!');
    }
  });
  $('#modalAgregarRegistro').modal('hide');
}


// ACTUALIZAR EXISTENCIAS
$(document).ready(function () {
  $('.btnActualizarExistencias').click(function () {
    var nombreProducto = $(this).data('nombre');
    $('#modalActualizarExistencias').find('.modal-title').text('Actualizar existencias de ' + nombreProducto);
    $('#modalActualizarExistencias').modal('show');
    $('#modalActualizarExistencias').data('nombre-producto', nombreProducto);
  });
});
function guardarActualizarExistencias() {
  var nombreProducto = $('#modalActualizarExistencias').data('nombre-producto');
  var entradas = $('#entradas').val();
  var salidas = $('#salidas').val();
  $.ajax({
    url: '/ingredientes',
    method: 'PUT',
    data: {
      tipo_operacion: 'actualizar_existencias',
      nombreProducto: nombreProducto,
      entradas: entradas,
      salidas: salidas
    },
    success: function (response) {
      console.log('Registro guardado correctamente');
      location.reload();
      alert('¡Registro guardado correctamente!');
    },
    error: function (xhr, status, error) {
      console.error('Error al guardar el registro:', error);
      if (xhr.status === 400) {
        alert(xhr.responseJSON.error);
      } else {
        alert('¡Error al guardar el registro! Por favor, inténtalo de nuevo más tarde.');
      }
    }
  });
  $('#modalActualizarExistencias').modal('hide');
}


// EDITAR REGISTRO
$(document).ready(function () {
  $('.btnEditarInfo').click(function () {
    var nombreProducto = $(this).data('nombre');
    var precioProducto = $(this).data('precio');
    var descripcionProducto = $(this).data('descripcion');

    $('#modalEditarInfo').find('.modal-title').text('Editar información de ' + nombreProducto);

    $('#modalEditarInfo').data('nombre-producto', nombreProducto);

    $('#modalEditarInfo').modal('show');

    $('#editarNombre').val(nombreProducto);
    $('#editarPrecio').val(precioProducto);
    $('#editarDescripcion').val(descripcionProducto);
  });
});
function guardarEditarInfo() {
  var nombreProducto = $('#modalEditarInfo').data('nombre-producto');
  var newNombre = $('#editarNombre').val();
  var newPrecio = $('#editarPrecio').val();
  var newDescripcion = $('#editarDescripcion').val();
  $.ajax({
    url: '/ingredientes',
    method: 'PUT',
    data: {
      tipo_operacion: 'editar_informacion',
      nombreProducto: nombreProducto,
      newNombre: newNombre,
      newPrecio: newPrecio,
      newDescripcion: newDescripcion
    },
    success: function (response) {
      console.log('Registro guardado correctamente');
      location.reload();
      alert('¡Registro guardado correctamente!');
    },
    error: function (xhr, status, error) {
      console.error('Error al guardar el registro:', error);
      alert('¡Error al guardar el registro!');
    }
  });
  $('#modalEditarInfo').modal('hide');
}


// ELIMINAR REGISTRO
$(document).ready(function () {
  $('.btnEliminarRegistro').click(function () {
    var nombreProducto = $(this).data('nombre');
    $('#modalEliminarRegistro').find('.modal-body').text('Esto eliminará toda la información relacionada a ' + nombreProducto + '.');
    $('#modalEliminarRegistro').modal('show');
    $('#modalEliminarRegistro').data('nombre-producto', nombreProducto);
  });
});
function guardarEliminarRegistro() { 
  var nombreProducto = $('#modalEliminarRegistro').data('nombre-producto');
  $.ajax({
    url: '/ingredientes',
    method: 'DELETE',
    data: {
      nombreProducto: nombreProducto
    },
    success: function (response) {
      console.log('Registro eliminado correctamente');
      location.reload();
    },
    error: function (xhr, status, error) {
      console.error('Error al eliminar el registro:', error);
      location.reload();
    }
  });
  $('#modalEliminarRegistro').modal('hide');
}
