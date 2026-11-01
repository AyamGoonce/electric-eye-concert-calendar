(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.2217d4c211c73fa8.js","sha256":"2217d4c211c73fa87860e155735ce0d75a7c2c0b1d38eaf2813489f7a6f39453","count":2030,"publishedAt":"2026-11-01T13:40:23Z","state":"calendar-state.json","stateSha256":"cf351acf0654bf442efcf9ba10f502b803174c722704bd1a1dcf79f05fd8f965","sourceState":"calendar-source-state.json","sourceStateSha256":"66ffa7d1694e63ffde19215fdf2d0010b26aa31caf5780ba54e041e1d6a1c6a0"});
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
