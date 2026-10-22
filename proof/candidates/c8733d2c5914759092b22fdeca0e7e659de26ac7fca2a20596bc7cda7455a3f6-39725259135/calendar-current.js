(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.c8733d2c59147590.js","sha256":"c8733d2c5914759092b22fdeca0e7e659de26ac7fca2a20596bc7cda7455a3f6","count":2057,"publishedAt":"2026-10-22T05:00:05Z","state":"calendar-state.json","stateSha256":"349881fc2983cf560c88c5083002f6aa54cec5d2551cc4084c77e7ae40c64cbd","sourceState":"calendar-source-state.json","sourceStateSha256":"cdcfd96a6d51f2a9d5490136518218bdc78b9d2eeb85b551260d218afeca2ebe"});
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
