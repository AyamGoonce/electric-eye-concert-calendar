(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.3fb7aaac9fc539eb.js","sha256":"3fb7aaac9fc539ebf4507ef51482b3e7dfdb774c57379225a179e8e7c8981b26","count":2056,"publishedAt":"2026-10-20T00:26:45Z","state":"calendar-state.json","stateSha256":"bc8def1cda2b6b274a5e3daddc432fb38b1cf54738e8bb1eeeaad986429fcdd1","sourceState":"calendar-source-state.json","sourceStateSha256":"354b426ef5c4c274f4778eb1d383f0b95b2e4c22e3b8913355c63fa5b20b91a1"});
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
