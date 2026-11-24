(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.82228ea1aac85905.js","sha256":"82228ea1aac859056fa8299f9aeda7cbe58c3e6e791dba5c81ef4f97e99c11b6","count":2107,"publishedAt":"2026-11-24T13:52:33Z","state":"calendar-state.json","stateSha256":"56205f4cf7720e095051d5ac6d436128f873e0eda2ae669b6a513b822a1a0b29","sourceState":"calendar-source-state.json","sourceStateSha256":"5940afa9037ab1ed262e3151674db6556fe534e3bac15169c87f30d3834bc034"});
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
