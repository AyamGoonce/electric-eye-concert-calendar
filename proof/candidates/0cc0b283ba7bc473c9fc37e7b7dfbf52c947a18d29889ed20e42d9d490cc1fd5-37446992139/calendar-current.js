(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.0cc0b283ba7bc473.js","sha256":"0cc0b283ba7bc473c9fc37e7b7dfbf52c947a18d29889ed20e42d9d490cc1fd5","count":2195,"publishedAt":"2026-10-06T10:04:19Z","state":"calendar-state.json","stateSha256":"9ee2445ac4c6ce25967cfd291326de7b2245df6ebb6da7a41cfaab765142e19a","sourceState":"calendar-source-state.json","sourceStateSha256":"d66c9c58ccab14a81525aacb0aeb12a88beb0f200a3e3a9da47b28e703438a75"});
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
