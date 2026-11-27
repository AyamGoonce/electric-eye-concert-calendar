(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.65ddfb9e1e02cb95.js","sha256":"65ddfb9e1e02cb95b17f25de08ecf0cf28a85d79126c1fb674480ba03ca924a0","count":2106,"publishedAt":"2026-11-27T12:39:41Z","state":"calendar-state.json","stateSha256":"085d5b6d29d0cc81e21b6b3480eccec5ee52e00d053784c40fdc52d567ca551e","sourceState":"calendar-source-state.json","sourceStateSha256":"989bc97c45973752025d4955423e4848b5c0243a548460b7dc62ee6b15baa64a"});
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
