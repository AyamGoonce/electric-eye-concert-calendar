(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.a0726a0b9a60fdc2.js","sha256":"a0726a0b9a60fdc230c35aa3d5a4404762e0219e9e7c2348e8be91cc894147c2","count":2099,"publishedAt":"2026-11-15T20:43:17Z","state":"calendar-state.json","stateSha256":"61d34ebead6d9cec142cda85c6f200f2ffca6d1540a0ea946305d5a9fc89253e","sourceState":"calendar-source-state.json","sourceStateSha256":"ee5000f3272fddd120890e4e541f9c3674238ac58652ce223d9d7bcf1aca784a"});
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
