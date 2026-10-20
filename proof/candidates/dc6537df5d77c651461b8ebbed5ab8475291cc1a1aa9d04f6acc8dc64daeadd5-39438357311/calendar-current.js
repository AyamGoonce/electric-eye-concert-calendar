(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.dc6537df5d77c651.js","sha256":"dc6537df5d77c651461b8ebbed5ab8475291cc1a1aa9d04f6acc8dc64daeadd5","count":2079,"publishedAt":"2026-10-20T14:23:21Z","state":"calendar-state.json","stateSha256":"5b1732021200c73262401b81be4f3b099a9289837619b3aaa6f4f04577dff2c1","sourceState":"calendar-source-state.json","sourceStateSha256":"82a9598312f071a48724c8be28f297e46a1e5a569d5e1a10a3b7aadf54fc52d0"});
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
