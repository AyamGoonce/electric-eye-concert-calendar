(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.7d45e18ca4c03841.js","sha256":"7d45e18ca4c038416bb4841b45ceda54bdc89c9df5bc29c7875ed40124469940","count":2128,"publishedAt":"2026-09-23T11:45:49Z","state":"calendar-state.json","stateSha256":"e85e1ba81caa03b99522ddb7147bc9eaed39c95be4696e4e9ced1075c9f8bafa","sourceState":"calendar-source-state.json","sourceStateSha256":"fba1b2883d6a16590a10be2e69af3de9b84032fc971eb241512272bed0ecddf6"});
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
