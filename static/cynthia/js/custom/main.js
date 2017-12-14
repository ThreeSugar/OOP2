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

/* promise -> used it to make network request wait for the value to return
   latitude and longitude get from satellite
   const -> valuable not going to change
   line 3. if only the user browser support the geolocation APPI then i can get the user position
   line 4-5. get the user lat and lng
   line 6. return the user lat and lng
   line 7. if the user browser not support the API
   line 8. if the user denied the location
   line 12-14. if the user browser not support the API
   line 9-27. is use if the user don't want to type anything into the search bar
              get the user location using their IP address, like track their IP address
              to get the user city/region to use
   line 22. use the region name as the location
   line 29. when the pages is loading
   line 33-34. reverse, geocoding is taking the address converting it to coordinate
               import the google map file
   line 37-40. result everything is ok, it will return the location
   line 41. exact the address
   line 42. give a rough guide of the location
   line 44. if the location detail failed, it will throw back an error message, unable to get the user location
   The search location sentance will appear the address as the user type in the search bar(at the same time):
   line 58. when the user type on keyup, what the user is typing it will put it inside the search-location
   line 64-66. Focus -> if the search input is focus it will focus on what the user is typing
                        sth like when the user type it will auto clear the sentance address and the search bar
                        and show the address that the user is typing now
*/
