(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.997ff31f55742c5f.js","sha256":"997ff31f55742c5f82ef2880f9f9e54bc16e932c46ff3a4213b8fed0e034b9b8","count":2407,"publishedAt":"2026-09-10T08:50:09Z","state":"calendar-state.json","stateSha256":"2786aef27fa28ad786f356fba816c8dcc4cd34dc6d74abbe1aa1dba7b459a564"});
  var currentSource = document.currentScript && document.currentScript.src;
  window.ElectricEyeConcertManifest = manifest;
  document.dispatchEvent(new CustomEvent("ee:concert-manifest-ready", {detail:manifest}));
  var script = document.createElement("script");
  script.src = new URL(manifest.data, currentSource || window.location.href).href;
  script.onerror = function(){
    document.dispatchEvent(new CustomEvent("ee:concert-data-error", {detail:{reason:"data asset unavailable"}}));
  };
  document.head.appendChild(script);
}());
