(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.d1bb2cb7302484bc.js","sha256":"d1bb2cb7302484bccf1afd714878e5be420ec10dee9201e03a3d02912f32e774","count":2128,"publishedAt":"2026-09-30T05:39:37Z","state":"calendar-state.json","stateSha256":"baf231087fb2b9b0e1d5b381d55dbb74bbe4bfb3110a2f419161ec94105ffaa7","sourceState":"calendar-source-state.json","sourceStateSha256":"ba2c4c9f6662de27eaea4a2195918421ec18e758dbf52e0dd70d1cb926265fd6"});
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
