(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.da65bb609a3ddf73.js","sha256":"da65bb609a3ddf73805e78d0efbf7ca43a598b99769591d91baec5a3f9863104","count":1840,"publishedAt":"2026-08-27T09:59:38Z","state":"calendar-state.json","stateSha256":"faf915425a9288703a2ae61d607c862acabd75944b9e32efbbe54339d9d08ac3"});
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
