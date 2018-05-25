function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function getJson(url, data, successCallback, errorCallback, completeCallback) {
    $.ajax({
        dataType: "json",
        method: 'get',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback,
        complete: completeCallback
    });
}

function postJson(url, data, successCallback, errorCallback, completeCallback) {
    data['csrfmiddlewaretoken']=getCookie('csrftoken');
    $.ajax({
        dataType: "json",
        method: 'post',
        url: url,
        data: data,
        success: successCallback,
        error: errorCallback,
        complete: completeCallback
    });
}

function validate_passwords_match() {
    return $('#id_confirmPassword').val() === $('#id_password').val();
}

function getFormData($form){
    /* retorna la data del form en json*/
    var unindexed_array = $form.serializeArray();
    var indexed_array = {};
    $.map(unindexed_array, function(n, i){
        indexed_array[n['name']] = n['value'];
    });
    return indexed_array;
}

function toTimeUnix( date, hour) {
    /*los parametros son los values de los inputs !!! */
    date = new Date(date);
    hora = hour.split(":");
    date.setHours(hora[0], hora[1]);
    return date.getTime() / 1000;
}


function insert_user_data(data_user){
    $("#fname").html("Nombre:  " + data_user.nombre);
    $("#lname").html("Apellido:  " + data_user.apellido);
    $("#dni").html("DNI:  " + data_user.dni);
    $("#email").html("E-mail:  " + data_user.mail);
    $("#birthday").html("Fecha de nacimiento:  " + data_user.fecha_de_nacimiento);
}

function insert_credit_card_data(data) {

    var card = data.get_tarjetas_de_credito;
    if (card !== null){
        $("#tarjetas").html('');
        for (i = 0; i < card.length; i++) {
            output = '';
            output += '<div id="tarjeta_' + i + '"> Tarjeta ' + i;
            output += '<p> Fecha de vencimiento:  ' + card[i].fecha_de_vencimiento + '</p>';
            output += '<p> Fecha de creacion:  ' + card[i].fecha_de_creacion + '</p>';
            output += '<p> Numero de tarjeta:  ' + card[i].numero + '</p>';
            output += '<p> CCV:  ' + card[i].ccv + '</p>';
            output += '<input hidden name="id_tarjeta_'+ i +'" value="' + card[i].id + '">';
            output += '</div>';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_tarjeta('+i+')">Editar datos</button>';
            output += '<button type="button" class="btn" onclick="eliminar_tarjeta_credito('+card[i].id+')">Borrar tarjeta</button>';
            output += '<hr>';
            $("#tarjetas").append(output);
        }
    }
}

function insert_cuenta_bancaria_data(data) {
    var cuentas = data.get_cuentas_bancarias;
    if (cuentas !== null){
        $("#cuentas_bancarias").html('');
        for (i=0; i < cuentas.length; i++){
            output='';
            output += '<div id="cuenta_' + i +'"> Cuenta ' + i;
            output += '<p> Entidad:  '+cuentas[i].entidad+'</p>';
            output += '<p> CBU:  '+cuentas[i].cbu+'</p>';
            output += '<input hidden name="id_cuenta_'+ i +'" value="' + cuentas[i].id + '">';
            output += '</div>';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_cuenta_bancaria('+i+')">Editar datos</button>';
            output += '<button type="button" class="btn"  onclick="eliminar_cuenta_bancaria('+cuentas[i].id+')" >Borrar Cuenta</button>';
            output += '<hr>';
            $("#cuentas_bancarias").append(output);
        }
    }
}





//completar vehiculo
function insert_vehicle_data(data) {
    var autos = data.get_vehiculos;
    $("#autos").html('');
    if (autos !== null){
        for (i=0; i < autos.length; i++){
            output='';
            output += '<div id="auto_' + i +'"> Auto ' + i;
            output += '<input hidden name="id_auto_'+ i +'" value="' + autos[i].id + '">';
            output += '<p> Marca:  '+autos[i].marca+'</p>';
            output += '<p> Modelo:  '+autos[i].modelo+'</p>';
            output += '<p> Capacidad:  '+autos[i].capacidad+'</p>';
            output += '<p> Dominio:  '+autos[i].dominio+'</p>';
            output += '</div>';
            output += '<button type="button" class="btn" onclick="trigger_modal_modificar_vehiculo('+i+')">Editar datos</button>';
            output += '<button type="button" class="btn"  title="aun nada">Borrar auto</button>';
            output += '<hr>';
            $("#autos").append(output);
        }
    }
}

function trigger_modal_agregar(id){
    $(id).modal('show');
}

function trigger_modal_modificar_usuario(datos) {
    $("#modal_fname").val(datos.usuario.nombre);
    $("#modal_lname").val(datos.usuario.apellido);
    $("#modal_dni").val(datos.usuario.dni);
    $("#modal_email").val(datos.usuario.mail);
    $("#modal_brithday").html('<input id="modal_brithday" class="form-control" type="date" required name="birthDay" value="'+datos.usuario.fecha_de_nacimiento+'">');
    $("#id_info_user").modal('show');
}

function trigger_modal_modificar_tarjeta(tarjeta) {
    d = datos.get_tarjetas_de_credito[tarjeta];
    $("#modal_id_tarjeta").val(d.id);
    $("#modal_num_tarjeta").val(d.numero);
    $("#modal_dateVto").val(d.fecha_de_vencimiento);
    $("#modal_dateCreation").val(d.fecha_de_creacion);
    $("#modal_ccv").val(d.ccv);
    $("#id_modal_modificar_tarjeta").modal('show');
}

function trigger_modal_modificar_cuenta_bancaria(cuenta) {
    d = datos.get_cuentas_bancarias[cuenta];
    $("#modal_id_cuenta").val(d.id);
    $("#modal_entidad").val(d.entidad);
    $("#modal_codigo_cbu").val(d.cbu);
    $("#id_modal_modificar_cuenta").modal('show');
}

function trigger_modal_modificar_vehiculo(auto) {
    console.log('entra');
    d = datos.get_vehiculos[auto];
    $("#modal_id_auto").val(d.id);
    $("#modal_marca").val(d.marca);
    $("#modal_modelo").val(d.modelo);
    $("#modal_capacidad").val(d.capacidad);
    $("#modal_dominio").val(d.dominio);
    $("#id_modal_modificar_auto").modal('show');
}
