(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.ad72bef38a39d3a7.js","sha256":"ad72bef38a39d3a768a731d8e88cfacea01a98ba6dedcae38ea7ce13d46959f2","count":2191,"publishedAt":"2026-11-11T10:18:13Z","state":"calendar-state.json","stateSha256":"11cedf12b8dbe3819d724647a1c62a452aa87a199a33d76d73559804ce3edce9","sourceState":"calendar-source-state.json","sourceStateSha256":"d94e18b7ab928074bd4180ffdc0ab68c516cec6b45896734f796a1032636adaf"});
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
