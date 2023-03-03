let get_sections_flats = function(house, section=undefined, flat=undefined){
        $.ajax({
            headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_section_flat',
                data: {'house': house},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    let sections = answer['sections'];
                    $('#id_section').empty();
                    $('#id_flat').empty();
                    $('#id_section').append($('<option>'));
                    for(let i=0;i<sections.length;i++){
                        console.log(sections[i]);
                        if (sections[i]['id'] == section){
                            $('#id_section').append($('<option>', { value : sections[i]['id'], selected : 'selected' }).text(sections[i]['name']));
                        }
                        else{
                            $('#id_section').append($('<option>', { value : sections[i]['id'] }).text(sections[i]['name']));
                        }
                    }

                    let flats = answer['flats'];
                    $('#id_flat').append($('<option>'));
                    for(let i=0;i<flats.length;i++){
                        console.log(flats[i]);
                        if (flats[i]['id'] == flat) {
                            $('#id_flat').append($('<option>', {value: flats[i]['id'], selected : 'selected'}).text(flats[i]['number']));
                        }
                        else{
                            $('#id_flat').append($('<option>', {value: flats[i]['id']}).text(flats[i]['number']));
                        }
                    }
                }
        });
    }

    let get_flats = function (section){
            $.ajax({
                headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_flats',
                data: {'section': section},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    let flats = answer['flats'];
                    $('#id_flat').empty();
                    $('#id_flat').append($('<option>'));
                    for(let i=0;i<flats.length;i++){
                        console.log(flats[i]);
                        $('#id_flat').append($('<option>', { value : flats[i]['id'] }).text(flats[i]['number']));
                    }

                },
                error: function (responce){
                    $('#id_flat').empty();
                }
            });
        }
    let get_owner = function (flat){
        $.ajax({
            headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_owner',
                data: {'flat': flat},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    console.log(response)
                    $('#user-fullname').html("<a href='/admin/update_owner/"+answer['owner']['id']+"'>"+answer['owner']['fullname']+"</a");
                    $('#user-phone').html("<a href=''>"+answer['owner']['phone']+"</a>");
                    $('#id_bankbook').val(answer['owner']['bankbook']);
                    $('#id_tariff').val(answer['owner']['tariff'])

                },
                error: function (responce){
                    console.log('error get_owner');
                }
        });
    }

    let get_flats_by_owner = function (owner){
            $.ajax({
                headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_flats_by_owner',
                data: {'owner': owner},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    let flats = answer['flats'];
                    $('#id_flat').empty();
                    $('#id_flat').append($('<option>'));
                    for(let i=0;i<flats.length;i++){
                        console.log(flats[i]);
                        $('#id_flat').append($('<option>', { value : flats[i]['id'] }).text(flats[i]['number']+', '+flats[i]['house__name']));
                    }

                },
                error: function (responce){
                    $('#id_flat').empty();
                }
            });
        }

        let get_flats_by_level = function (level){
            $.ajax({
                headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_flats',
                data: {'level': level},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    let flats = answer['flats'];
                    $('#id_flat').empty();
                    $('#id_flat').append($('<option>'));
                    for(let i=0;i<flats.length;i++){
                        console.log(flats[i]);
                        $('#id_flat').append($('<option>', { value : flats[i]['id'] }).text(flats[i]['number']));
                    }

                },
                error: function (responce){
                    $('#id_flat').empty();
                }
            });
        }

        let get_sections_levels = function (house, section=undefined, level=undefined){
            $.ajax({
                headers: { "X-CSRFToken": '{{ csrf_token }}' },
                type: "GET",
                url: '/admin_app/get_section_level',
                data: {'house': house},
                contentType: 'json/application',
                success: function(response){
                    let answer = JSON.parse(response);
                    let sections = answer['sections'];
                    $('#id_section').empty();
                    $('#id_level').empty();
                    $('#id_section').append($('<option>'));
                    for(let i=0;i<sections.length;i++){
                        console.log(sections[i]);
                        if (sections[i]['id'] == section){
                            $('#id_section').append($('<option>', { value : sections[i]['id'], selected : 'selected' }).text(sections[i]['name']));
                        }
                        else{
                            $('#id_section').append($('<option>', { value : sections[i]['id'] }).text(sections[i]['name']));
                        }
                    }

                    let levels = answer['levels'];
                    $('#id_level').append($('<option>'));
                    for(let i=0;i<levels.length;i++){
                        console.log(levels[i]);
                        if (levels[i]['id'] == level) {
                            $('#id_level').append($('<option>', {value: levels[i]['id'], selected : 'selected'}).text(levels[i]['name']));
                        }
                        else{
                            $('#id_level').append($('<option>', {value: levels[i]['id']}).text(levels[i]['name']));
                        }
                    }
                },
                error: function (responce){
                    $('#id_section').empty();
                    $('#id_level').empty();
                }
            });
        }