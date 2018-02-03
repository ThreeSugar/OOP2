const getUserLocation = new Promise((resolve, reject) => {
    if(navigator.geolocation) {
        navigator.geolocation.getCurrentPosition((position) => {
            const lat = position.coords.latitude;
            const lon = position.coords.longitude;
            return resolve({lat, lon});
        }, (error) => {
            if (error.code == error.PERMISSION_DENIED) {
                return reject('Permission Error');
            }
        });
    } else {

        return reject('Unable to get position');
    }
});


const getLocationFromIp = new Promise((resolve, reject) => {
    return $.getJSON('http://ip-api.com/json', (response) => {
        if(response) {
            return resolve(response.regionName);
        } else {
            return reject('Unable to get address from IP');
        }
    });
});

$(document).ready(() => {
    console.log('Getting here for sure')
    getUserLocation.then((locationData) => {
        if(locationData) {
            const geocoder = new google.maps.Geocoder();
            const latLng = new google.maps.LatLng(locationData.lat, locationData.lon);
         
            if (geocoder) {
               geocoder.geocode({ 'latLng': latLng}, (results, status) => {
                  if (status == google.maps.GeocoderStatus.OK) {
                     console.log(locationData);
                     console.log(results);
                     $('#search-location').val(results[0].formatted_address)
                     $('#user-location').text(results[4].formatted_address);                     
                  }
                  else {
                     console.log("Geocoding failed: " + status);
                  }
               });
            }    
        }
    }).catch((err) => {
        console.log(err)
        getLocationFromIp.then((location) => {
            $('#user-location').text(location);
        })
    });

  
    $('#search-location').on('keyup', (e) => {
        const currentlyEnteredLocation = $('#search-location').val();

        $('#user-location').text(currentlyEnteredLocation); 
    });

    $('#search-location').on('focus', () => {
        const currentlyEnteredLocation = $('#search-location').val('');        
    });
});


