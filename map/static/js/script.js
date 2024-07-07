const URL_PREFIX = "";
var GEO_LAYER = null;
var ACTIVE_POLIGONS = [];
var MARKERS = [];
var last_selected_mark = null;
var HEAT_LAYER = null;


function remove_all_markers(){
  for (marker of MARKERS){
    marker.remove();
  }
}

var osmUrl = 'http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
            osmAttrib = '&copy; <a href="http://openstreetmap.org/copyright">OpenStreetMap</a> contributors',
            osm = L.tileLayer(osmUrl, { maxZoom: 18, attribution: osmAttrib }),
            map = new L.Map('map', { center: new L.LatLng(55.751244, 37.621409), zoom: 10 }),
            drawnItems = L.featureGroup().addTo(map);
  
    L.control.layers({
        'osm': osm.addTo(map)
    }).addTo(map);


    map.on(L.Draw.Event.CREATED, function (event) {
        var layer = event.layer;
        layer.setStyle({color: "#9933ff"});
        layer.setStyle({fillColor: "#7300e6"});
        layer.options.name = "user";
        layer.on("click", onPolyClick);
        drawnItems.addLayer(layer);
    });

    var GEO_CONTROL = new L.Control.Draw({
      edit: {
          featureGroup: drawnItems,
          poly: {
              allowIntersection: true
          }
      },
      draw: {
          polygon: {
              allowIntersection: true,
              showArea: true
          },
          polyline: false,
          circle: false, // Turns off this drawing tool
          rectangle: false,
          marker: false
      }
    });




var MAP_MARKERS = {};
var PREDICTED_MARKER_IDS = [];




(async function Ge0() {
  const data = await fetch(
    URL_PREFIX + `/api/sendgeo`, {
      method: `POST`,
  
      headers: {
        "content-type": `application/json`
      }
      

    });
    let Feature = await  data.json();
    GEO_LAYER = L.geoJSON(Feature, {
      style: (feature) => {
        return {
          stroke: true,
          color: "#9933ff",
          weight: 2,
          opacity: 0.7,
          fill: true,
          fillColor: "#7300e6",
          fillOpacity: 0.15,
          smoothFactor: 0.5,
          interactive: true,
        };
        
      },
      onEachFeature: function(feature,layer){
        layer.options.name = feature.properties.NAME;
        layer.options.coordinates = feature.geometry.coordinates;
        layer.on('click', (e) => onPolyClick(e));
      },
    });
    
  })();

function ShowPoligoneMap(){
  remove_all_markers();
  map_container = document.getElementById("map");
  let field = document.getElementById("predCount-input");
  field.classList.remove("d-none");
  map.removeLayer(HEAT_LAYER);
  map.addLayer(GEO_LAYER);
  map.addLayer(drawnItems);
  map.addControl(GEO_CONTROL);
  map.invalidateSize();
}

function onPolyClick(evt) {
  let poly = evt.target;
  if (ACTIVE_POLIGONS.includes(poly)){
    ACTIVE_POLIGONS = ACTIVE_POLIGONS.filter(function(e) { return e !== poly });
    poly.setStyle({fillColor: "#7300e6"});
    poly.setStyle({fillOpacity: 0.15});
  }
  else{
  ACTIVE_POLIGONS.push(poly);
  poly.setStyle({fillColor: '#e83e8c'});
  poly.setStyle({fillOpacity: 0.5});

  }
  console.log(poly.options.coordinates);
}





var greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});
var blueIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});


L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
document.getElementsByClassName('leaflet-control-attribution')[0].style.display = 'none';



function HideMap(){
  remove_all_markers();
  let field = document.getElementById("predCount-input");
  field.classList.add("d-none");
  map_container = document.getElementById("map");
  map.removeLayer(GEO_LAYER);
  map.removeLayer(drawnItems);
  map.removeControl(GEO_CONTROL);
  map.addLayer(HEAT_LAYER);
  map.invalidateSize();

}


function ShowMap(){
  remove_all_markers();
  map_container = document.getElementById("map");
  let field = document.getElementById("predCount-input");
  field.classList.remove("d-none");
  map.removeLayer(GEO_LAYER);
  map.removeLayer(drawnItems);
  map.removeLayer(HEAT_LAYER);
  map.removeControl(GEO_CONTROL);
  map.invalidateSize();

}


function show_predict_warning(w){
  var yellow_warnings = document.getElementById("list-mark-predict-warnings");
  var warning = yellow_warnings.getElementsByClassName(w)[0];
  warning.classList.remove("d-none");
}


const decodeUnicode = (str) => {
	return str.replace(/\\u([a-fA-F0-9]{4})/g, function (match, grp) {
		return String.fromCharCode(parseInt(grp, 16));
	});
};

async function Predict()
{
  remove_all_markers()
  remove_all_warnings();
  let polygon_radio = document.querySelector('#inlinemapRadio3:checked');
  let heat_radio = document.querySelector('#inlinemapRadio2:checked');

  if (!heat_radio){
  var number = document.getElementById("predCount-input").getElementsByTagName("input")[0].value;
  }
  var gender = document.getElementById("sex-param").value;
  var incomes = document.getElementById("income-param").getElementsByClassName("form-check-input");
  var income = '';
  var start_age = document.getElementById("age-coodinate-field1").value;
  var end_age = document.getElementById("age-coodinate-field2").value;
  
  for (el of incomes){
    if (el.checked)
      income += el.value;
  }

  console.log(polygon_radio);
  if (polygon_radio){

    if (!(number && income && start_age && end_age && gender != "null" && isNumeric(number) && isNumeric(start_age) && isNumeric(end_age))) {
      show_predict_warning("form_warning");

      return;
    }
    number = parseInt(number);
    start_age = parseInt(start_age);
    end_age = parseInt(end_age);

      if (!ACTIVE_POLIGONS.length){
        show_predict_warning("form_warning");
        return;
      }
      remove_all_warnings();
      show_predict_warning("wait-warning")
      const response = await fetch( URL_PREFIX + "/api/predict", {
        method: "POST", 
        headers: {
          "Content-Type": "application/json",
        },
        body :JSON.stringify({
          number : number,
          params : {
            gender : gender,
            income : income,
            ageFrom : start_age,
            ageTo : end_age
          },
          coordinates : ACTIVE_POLIGONS.map((el) => el.options.coordinates)

        })
        
      });

      var data = await response.json();
      for (element of data["predicted_coordinates"]){
      var map_marker = new L.marker([
        element[0],
        element[1]
      ] ).bindPopup(`<p>Охват ${element[2]}</p>`).addTo(map);
      map_marker._icon.style.filter = "hue-rotate(150deg)";
      MARKERS.push(map_marker)
    }
      remove_all_warnings();
      show_predict_warning("green-warning")
      return;
}
else if (heat_radio){



  if (!( income && start_age && end_age && gender != "null" && isNumeric(start_age) && isNumeric(end_age))) {
    show_predict_warning("form_warning");
    return;
  }
  start_age = parseInt(start_age);
  end_age = parseInt(end_age);
  const response = await fetch( URL_PREFIX + '/api/heatmappredict', {
    method: "POST", 
    headers: {
      "Content-Type": "application/json",
    },
    body : JSON.stringify({
      params : {
        gender : gender,
        income : income,
        ageFrom : start_age,
        ageTo : end_age
      }
   })
   
  });

    const result = await response.json();
    map.removeLayer(HEAT_LAYER);
    HEAT_LAYER = L.heatLayer(result['predicted_coordinates'], {radius: 60, max : 1/15});  
    map.addLayer(HEAT_LAYER);



}

else{



  if (!(number && income && start_age && end_age && gender != "null" && isNumeric(number) && isNumeric(start_age) && isNumeric(end_age))) {
    show_predict_warning("form_warning");
    return;
  }

  number = parseInt(number);
    start_age = parseInt(start_age);
    end_age = parseInt(end_age);

  remove_all_warnings();
      show_predict_warning("wait-warning")
      const response = await fetch( URL_PREFIX + "/api/predict", {
        method: "POST", 
        headers: {
          "Content-Type": "application/json",
        },
        body :JSON.stringify({
          number : number,
          params : {
            gender : gender,
            income : income,
            ageFrom : start_age,
            ageTo : end_age
          },
        })
        
      });

      var data = await response.json();
      for (element of data["predicted_coordinates"]){
      var map_marker = new L.marker([
        element[0],
        element[1]
      ] ).bindPopup(`<p>Охват ${element[2]}</p>`).addTo(map);
      map_marker._icon.style.filter = "hue-rotate(150deg)";

      MARKERS.push(map_marker)
    }
      remove_all_warnings();
      show_predict_warning("green-warning")
      return;

}

  remove_all_warnings();
  show_predict_warning("green-warning")
}


(async function load_heat_to_client(){

    const response = await fetch( URL_PREFIX + '/api/heatmappredict', {
      method: "POST", 
      headers: {
        "Content-Type": "application/json",
      },
      body : 
        JSON.stringify({
        params : {gender: 'all', ageFrom: 18, ageTo: 100, income: 'abc'}})

    });

      const result = await response.json();

      HEAT_LAYER = L.heatLayer(result['predicted_coordinates'], {radius: 60, max : 1/15});      
  console.log("Successfuly loaded");

    

})();






function ChangeActiveInMarkBar(el){

  remove_all_warnings();

}

function hide_yellow_warnings(){
  var yellow_warnings = document.getElementById("list-map-warnings");
  for (child of yellow_warnings.children){
    child.classList.add("d-none");
  }

}

function hide_red_warnings(){
  var red_warnings = document.getElementById("list-mark-submit-warnings");
  for (child of red_warnings.children){
    child.classList.add("d-none");
  }
  return;

}

function show_yellow_warning(w){
  var yellow_warnings = document.getElementById("list-map-warnings");
  var warning = yellow_warnings.getElementsByClassName(w)[0];
  warning.classList.remove("d-none");
}

function show_red_warning(w){
  var yellow_warnings = document.getElementById("list-mark-submit-warnings");
  var warning = yellow_warnings.getElementsByClassName(w)[0];
  warning.classList.remove("d-none");
}


function disable_mark_fields(){
  var fields = document.getElementById("mark-save-fields").getElementsByTagName("input");
  var save_button = document.getElementById("mark-save-fields").getElementsByTagName("button")[0];
  for (field of fields){
    field.setAttribute("disabled", "");
    field.value = "";
  }
  save_button.setAttribute("disabled", "");
}

function enable_mark_fields(){
  var fields = document.getElementById("mark-save-fields").getElementsByTagName("input");
  var save_button = document.getElementById("mark-save-fields").getElementsByTagName("button")[0];
  for (field of fields){
    field.removeAttribute("disabled");
  }
  save_button.removeAttribute("disabled");
}

function is_int(str){
  if (!str)
    return false;
  for (c of str){
    if (c >= '0' && c <= '9') {
      continue;
    }
    return false;
}
  return true;
}

function isNumeric(str) {
  if (typeof str != "string") return false
  return !isNaN(str) && 
         !isNaN(parseFloat(str)) 
}

function show_warning_text_add(w){
  var red_warnings = document.getElementById("list-mark-submit-warnings-text-add");
  var warning = red_warnings.getElementsByClassName(w)[0];
  warning.classList.remove("d-none");
}


function OnTabChange(){
  remove_all_warnings();

}


function show_file_warning(w)
{
  var yellow_warnings = document.getElementById("list-mark-submit-warnings-file");
  var warning = yellow_warnings.getElementsByClassName(w)[0];
  warning.classList.remove("d-none");
}

function remove_all_warnings()
{
  var warnings = document.getElementsByClassName("alert");
  for (warning of warnings){
    warning.classList.add("d-none");
  }

}
