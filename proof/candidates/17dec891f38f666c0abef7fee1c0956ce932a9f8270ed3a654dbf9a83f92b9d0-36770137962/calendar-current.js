(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.17dec891f38f666c.js","sha256":"17dec891f38f666c0abef7fee1c0956ce932a9f8270ed3a654dbf9a83f92b9d0","count":2233,"publishedAt":"2026-09-30T20:05:38Z","state":"calendar-state.json","stateSha256":"99ea47a73a57b59c28817338a889671e42d7e86121c67689d0e2582f88ca1eee","sourceState":"calendar-source-state.json","sourceStateSha256":"d7f1a93527b715171721c84be0157652123fb96fa6916b16ed97315da8df3c5c"});
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
