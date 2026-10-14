(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.41e81348b22b786d.js","sha256":"41e81348b22b786d970198120a15ed35528815b22652734f43159c930940d2e1","count":2160,"publishedAt":"2026-10-14T21:48:28Z","state":"calendar-state.json","stateSha256":"4bc8a6da639f560b12fd338249dd12fd0e833787c27d2082e767d683eedecbb4","sourceState":"calendar-source-state.json","sourceStateSha256":"84cb988aad129bb8d33434d088f91e07b19b27076643571447a76bf24b175b3d"});
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
