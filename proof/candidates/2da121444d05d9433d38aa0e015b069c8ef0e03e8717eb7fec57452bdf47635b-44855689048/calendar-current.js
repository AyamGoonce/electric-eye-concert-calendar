(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2da121444d05d943.js","sha256":"2da121444d05d9433d38aa0e015b069c8ef0e03e8717eb7fec57452bdf47635b","count":2121,"publishedAt":"2026-11-21T02:24:33Z","state":"calendar-state.json","stateSha256":"06b5925fd83b7905fdc44ca35b049740c17239c0c7ff04dc66709791e6adff5c","sourceState":"calendar-source-state.json","sourceStateSha256":"19230217622850be63126f2b70cebe1e20cb7bab67a66290e3e60642a606265d"});
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
