(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dc0b1f4828d44b6c.js","sha256":"dc0b1f4828d44b6c540f5e313fea768ac280be4861ef28abbc96f60595ba80ea","count":2232,"publishedAt":"2026-09-30T20:16:32Z","state":"calendar-state.json","stateSha256":"b107497418987dcd5f7f7062963fddbd7630e245fefc01f01274e3a12d0b16b8","sourceState":"calendar-source-state.json","sourceStateSha256":"82e50edab82c38027296a4fbc8715d10997b00b3b790ce1a39fdf4151b567345"});
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
