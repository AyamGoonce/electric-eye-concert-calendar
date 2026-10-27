(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2ee60bd0b6345112.js","sha256":"2ee60bd0b634511288961cb045abd78b88c00e477944e4ce8426c9c33c7e9b5e","count":2041,"publishedAt":"2026-10-27T09:08:57Z","state":"calendar-state.json","stateSha256":"52253537faa62446736a5a54ade96ea21464e9ffdf0bc09ba3fc9ec6b9f6e57e","sourceState":"calendar-source-state.json","sourceStateSha256":"b07e4c18b99f2a76047b7917902e2f73fb62aec6e2df67f79a7da3f72772204d"});
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
