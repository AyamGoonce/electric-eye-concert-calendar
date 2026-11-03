(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.1fbad8c3baecd0a6.js","sha256":"1fbad8c3baecd0a61ebba3f2de3f398626824fb4ba10d6bc62db3df75b33631a","count":2056,"publishedAt":"2026-11-03T23:30:46Z","state":"calendar-state.json","stateSha256":"24498d697dfdfb468abaa7fabf41cc8dcc97302f4c02ad45a3c3cacfc8f1ef0e","sourceState":"calendar-source-state.json","sourceStateSha256":"a21130193c417b27159d4590f61997ff6790df0b63c70b497ac45b02d5ae5c17"});
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
