(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.b10c19bf56f4a9d8.js","sha256":"b10c19bf56f4a9d8ff2470ec4606e859b42bc55f137b4a5cf4310284bb40e99c","count":2127,"publishedAt":"2026-10-16T21:19:50Z","state":"calendar-state.json","stateSha256":"9af036967412eff8a80f090a83000540c8c1fd06c389b28b6fdc6be6451f2dcd","sourceState":"calendar-source-state.json","sourceStateSha256":"525ce0d094ada1d2d925d29a6c59991b54f5f86ecd2d3aee335cad2078d61f76"});
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
