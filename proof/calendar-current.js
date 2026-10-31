(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.6da809b42e151c08.js","sha256":"6da809b42e151c08934f610a8c49a5ff8cac186879f40d77b1d35467de6d0ddc","count":2057,"publishedAt":"2026-10-31T12:44:41Z","state":"calendar-state.json","stateSha256":"8e5a897edcdedfdf4105d647a32b6ca87ff2a2ffd3684cc1665b0f895ba3ebf5","sourceState":"calendar-source-state.json","sourceStateSha256":"204e2fee6f297acacc4041e3b39cb50c5a2a9afb969f05ceec6081895bea8bb1"});
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
