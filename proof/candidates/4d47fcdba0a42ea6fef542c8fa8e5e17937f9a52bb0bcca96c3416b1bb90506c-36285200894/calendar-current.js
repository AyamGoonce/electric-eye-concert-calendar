(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.4d47fcdba0a42ea6.js","sha256":"4d47fcdba0a42ea6fef542c8fa8e5e17937f9a52bb0bcca96c3416b1bb90506c","count":2069,"publishedAt":"2026-09-27T01:20:20Z","state":"calendar-state.json","stateSha256":"9d50aeb3ff756de350382501b1e09d1623ad33b32c11febd580e0f32bf59b3eb","sourceState":"calendar-source-state.json","sourceStateSha256":"65842fbb33abbaf2af42a6ae37da539c7225e19b9a559a5a03cd0836d6c1189e"});
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
