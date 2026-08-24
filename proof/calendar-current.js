(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.cc77e1e334d699fb.js","sha256":"cc77e1e334d699fb9d42c53e6352b12553f9a6a123b1e1fb32e47a8f7859c7ec","count":1735,"publishedAt":"2026-08-24T13:21:23Z","state":"calendar-state.json","stateSha256":"cf1b77ea8f811946f24e1ee12523d5bb3e6a701164199f5b337365579c828268"});
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
