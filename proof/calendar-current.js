(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.90e360038febc6cc.js","sha256":"90e360038febc6cc33948a3be2f344752f63407d68bcd5d78c96f0401b8dfc6e","count":2087,"publishedAt":"2026-10-22T21:44:27Z","state":"calendar-state.json","stateSha256":"2ad4c79a0490ebd249b6a8a49c79c46608fa4230de57f69743cfde6887065aa8","sourceState":"calendar-source-state.json","sourceStateSha256":"1a35ce14d2bd27da6c7e9a0d04790c05fdb454fee1071af3871509fef1c8f5db"});
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
