(function(){
  "use strict";
  var manifest = Object.freeze({"data":"calendar-data.65571f718f7543dd.js","sha256":"65571f718f7543dd44f2d239ceff3e6cd1f602a8a592fa43fb738a0bc418fd56","count":2223,"publishedAt":"2026-10-01T10:14:44Z","state":"calendar-state.json","stateSha256":"839c620ab517c1d9ba76beb6c040c35c71e5c48653c465b1063a6ee7085bbf24","sourceState":"calendar-source-state.json","sourceStateSha256":"642ddd3ecbb6773eba99f52fdaa72ef97d41f935e993ad249314e859b13b49ad"});
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
