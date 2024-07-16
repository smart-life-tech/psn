$(document).ready(function() {
    $('#configForm').submit(function(event) {
        event.preventDefault();
        $.post('/configure', $(this).serialize(), function(response) {
            alert(response);
        });
    });

    $('#oscMappingForm').submit(function(event) {
        event.preventDefault();
        $.post('/add_osc_mapping', $(this).serialize(), function(response) {
            alert(response);
            $('#mappingList').empty(); // Clear existing list
            fetchMappings(); // Refresh mappings list after adding
        }).fail(function(jqXHR, textStatus, errorThrown) {
            alert('Error adding OSC mapping: ' + jqXHR.responseText);
        });
    });

    $('#sacnMappingForm').submit(function(event) {
        event.preventDefault();
        $.post('/add_sacn_mapping', $(this).serialize(), function(response) {
            alert(response);
            $('#mappingList').empty(); // Clear existing list
            fetchMappings(); // Refresh mappings list after adding
        }).fail(function(jqXHR, textStatus, errorThrown) {
            alert('Error adding SACN mapping: ' + jqXHR.responseText);
        });
    });

    $('#startButton').click(function() {
        $.post('/start', function(response) {
            alert(response);
        });
    });

    $('#stopButton').click(function() {
        $.post('/stop', function(response) {
            alert(response);
        });
    });

    $('#refreshButton').click(function() {
        $('#mappingList').empty(); // Clear existing list
        fetchMappings(); // Refresh mappings list
    });

    // Fetch existing mappings on page load
    fetchMappings();

    function fetchMappings() {
        $.get('/mappings', function(response) {
            console.log("Mappings fetched: ", response.mappings);
            response.mappings.forEach(function(mapping, index) {
                var listItem = $('<li>').text(`Tracker ID: ${mapping.tracker_id}, Type: ${mapping.type}`);
                var deleteButton = $('<button>').text('Delete').click(function() {
                    console.log("Delete button clicked for index: ", index);
                    deleteMapping(index);
                });
                listItem.append(deleteButton);
                $('#mappingList').append(listItem);
            });
        });
    }

    function deleteMapping(index) {
        $.ajax({
            url: `/delete_mapping/${index}`,
            type: 'DELETE',
            success: function(response) {
                console.log("Mapping deleted: ", response);
                alert(response);
                $('#mappingList').empty(); // Clear existing list
                fetchMappings(); // Refresh mappings list after deletion
            },
            error: function(xhr, status, error) {
                console.log("Error deleting mapping: ", error);
                alert('Error deleting mapping');
            }
        });
    }
});
