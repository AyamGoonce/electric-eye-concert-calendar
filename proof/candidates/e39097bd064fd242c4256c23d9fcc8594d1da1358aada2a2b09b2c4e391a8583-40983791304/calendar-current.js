(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.e39097bd064fd242.js","sha256":"e39097bd064fd242c4256c23d9fcc8594d1da1358aada2a2b09b2c4e391a8583","count":2026,"publishedAt":"2026-10-30T01:08:56Z","state":"calendar-state.json","stateSha256":"b21645a77e805bd2f09c09c66d650346deee9085f6383cc9f109a4fe903ce120","sourceState":"calendar-source-state.json","sourceStateSha256":"a1f0b9a12aae6273542bb7a889075c9fcbd7bde2a9bf2eb22527dda12783d989"});
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
