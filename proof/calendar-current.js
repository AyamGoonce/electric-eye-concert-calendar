(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6cbf6cf3f0a14d36.js","sha256":"6cbf6cf3f0a14d36bcd33a93262b647a5a4ade8afe50f2014feff3a4453841a5","count":2121,"publishedAt":"2026-11-27T23:30:23Z","state":"calendar-state.json","stateSha256":"899dcc1068780a3ae0ec8ac1b20ab62b30ddd10ca215211996bc8eef6f302551","sourceState":"calendar-source-state.json","sourceStateSha256":"1336b50a3312c4f7e8a029fcc4348b37a46e43f813c46d267da4d1e3efab7bd4"});
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
